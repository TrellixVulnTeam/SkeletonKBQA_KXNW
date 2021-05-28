
import numpy as np
import torch
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from skeleton_parsing.models_bert import model_utils
from skeleton_parsing.models_bert.fine_tuning_based_on_bert.run_sequence_classifier import \
    QuestionTypeProcessor, convert_examples_to_features
from skeleton_parsing.models_bert.pytorch_pretrained_bert import BertTokenizer
from skeleton_parsing.models_bert.pytorch_pretrained_bert.modeling import BertForSequenceClassification
from skeleton_parsing.skeleton_args import bert_args
from common.globals_args import q_mode


processors = {"question_type": QuestionTypeProcessor}
task_name = "question_type"
args = model_utils.run_sequence_classifier_get_local_args()

processor = processors[task_name]()

if q_mode == 'cwq':
    label_list = ["comparative","superlative","composition","conjunction"] #cwq
elif q_mode == 'graphq':
    label_list = ["bgp", "count", "superlative", "comparative"]  # graphq
elif q_mode == 'lcquad':
    label_list = ["bgp","ask","count"] #lc
else:
    label_list = processor.get_labels()

num_labels_task = {"question_type":len(label_list)}
num_labels = num_labels_task[task_name]
tokenizer = BertTokenizer.from_pretrained(bert_args.bert_base_cased_tokenization, do_lower_case=args.do_lower_case)
# label_ids_map = {label: i for i, label in enumerate(label_list)}
ids_label_map = {i: label for i, label in enumerate(label_list)}

bert_fine_tuning_filepath = bert_args.fine_tuning_qtype_classifier_G_model
model_state_dict = torch.load(bert_fine_tuning_filepath, map_location='cpu')
model = BertForSequenceClassification.from_pretrained(args.bert_model, state_dict=model_state_dict, num_labels=num_labels)
device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
model.to(device)


def process(line_a, line_b=None):
    eval_examples = processor.get_simple_examples(line_a=line_a, line_b=line_b)
    eval_features = convert_examples_to_features(eval_examples, label_list, args.max_seq_length, tokenizer)
    all_input_ids = torch.tensor([f.input_ids for f in eval_features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in eval_features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in eval_features], dtype=torch.long)
    all_label_ids = torch.tensor([f.label_id for f in eval_features], dtype=torch.long)
    eval_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.eval_batch_size)
    model.eval()
    outputs = []
    for input_ids, input_mask, segment_ids, label_ids in eval_dataloader:
        input_ids = input_ids.to(device)
        input_mask = input_mask.to(device)
        segment_ids = segment_ids.to(device)
        with torch.no_grad():
            logits = model(input_ids, segment_ids, input_mask)
        logits = logits.detach().cpu().numpy()
        outputs = np.argmax(logits, axis=1)
    return ids_label_map[outputs[0]]


if __name__ == "__main__":
    classifier_label = process(line_a='What degree is held by a notable person who was educated at State Elementary School Menteng 01 ?')
    print(classifier_label)



