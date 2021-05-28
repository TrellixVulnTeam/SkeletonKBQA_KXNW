import torch

from tqdm import tqdm
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from skeleton_parsing.models_bert.pytorch_pretrained_bert.tokenization import BertTokenizer
from skeleton_parsing.models_bert.pytorch_pretrained_bert.modeling import BertForQuestionAnswering
from skeleton_parsing.models_bert.fine_tuning_based_on_bert.run_redundancy_span import read_one_example, \
    convert_examples_to_features, RawResult, write_span_headwords_with_nbest
from skeleton_parsing.models_bert import model_utils
from skeleton_parsing.skeleton_args import bert_args


model_file = bert_args.fine_tuning_redundancy_span_D_model
args = model_utils.run_redundancy_span_get_local_args()

tokenizer = BertTokenizer.from_pretrained(args.bert_model)
model_state_dict = torch.load(model_file, map_location='cpu')
model = BertForQuestionAnswering.from_pretrained(args.bert_model, state_dict=model_state_dict)
device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
model.to(device)


def simple_process(sequence):
    '''process one sequence, such as question'''
    eval_examples = read_one_example(one_line=sequence)
    eval_features = convert_examples_to_features(examples=eval_examples, tokenizer=tokenizer,
            max_seq_length=args.max_seq_length, doc_stride=args.doc_stride, max_query_length=args.max_query_length, is_training=False)
    all_input_ids = torch.tensor([f.input_ids for f in eval_features], dtype=torch.long)
    all_input_mask = torch.tensor([f.input_mask for f in eval_features], dtype=torch.long)
    all_segment_ids = torch.tensor([f.segment_ids for f in eval_features], dtype=torch.long)
    all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)
    eval_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_example_index)
    eval_sampler = SequentialSampler(eval_data)
    eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.predict_batch_size)
    model.eval()
    all_results = []
    for input_ids, input_mask, segment_ids, example_indices in tqdm(eval_dataloader, desc="Evaluating"):
        input_ids = input_ids.to(device)
        input_mask = input_mask.to(device)
        segment_ids = segment_ids.to(device)
        with torch.no_grad():
            batch_start_logits, batch_end_logits = model(input_ids=input_ids, token_type_ids=segment_ids, attention_mask=input_mask)
        for i, example_index in enumerate(example_indices):
            start_logits = batch_start_logits[i].detach().cpu().tolist()
            end_logits = batch_end_logits[i].detach().cpu().tolist()
            eval_feature = eval_features[example_index.item()]
            unique_id = int(eval_feature.unique_id)
            all_results.append(RawResult(unique_id=unique_id, start_logits=start_logits, end_logits=end_logits))
    span = write_span_headwords_with_nbest(eval_examples, eval_features, all_results,
                                           args.n_best_size, args.max_answer_length, args.do_lower_case, args.verbose_logging)
    return span


if __name__ == "__main__":
    span = simple_process(sequence='what are some common surnames of female people ?')
    print('123', span)
