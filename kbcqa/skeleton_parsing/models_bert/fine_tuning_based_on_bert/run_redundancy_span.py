import torch
import collections
import random
import numpy as np
import pickle
import json
import sys
import os

from tqdm import tqdm, trange
from torch.utils.data import TensorDataset, DataLoader, RandomSampler, SequentialSampler
from torch.utils.data.distributed import DistributedSampler

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
os.environ['CUDA_VISIBLE_DEVICES']='0'

from pytorch_pretrained_bert.tokenization import whitespace_tokenize, BertTokenizer
from pytorch_pretrained_bert.modeling import BertForQuestionAnswering
from pytorch_pretrained_bert.file_utils import PYTORCH_PRETRAINED_BERT_CACHE
from pytorch_pretrained_bert.optimization import BertAdam
import model_utils
from fine_tuning_based_on_bert import span_utils


class SequenceExample(object):
    '''a single training/test example for the sequence dataset.'''

    def __init__(self, qas_id, doc_tokens, orig_answer_text=None, start_position=None, end_position=None):
        self.qas_id = qas_id
        # self.question_text = question_text
        self.doc_tokens = doc_tokens
        # self.orig_index_to_pos = orig_index_to_pos
        self.orig_answer_text = orig_answer_text
        self.start_position = start_position
        self.end_position = end_position

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = ""
        s += "qas_id: %s" % (self.qas_id)
        s += ", doc_tokens: [%s]" % (" ".join(self.doc_tokens))
        if self.start_position: s += ", start_position: %d" % (self.start_position)
        if self.start_position: s += ", end_position: %d" % (self.end_position)
        return s


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, unique_id, example_index, doc_span_index, tokens, token_to_orig_map,
                 token_is_max_context, input_ids, input_mask, segment_ids, start_position=None, end_position=None):
        self.unique_id = unique_id
        self.example_index = example_index
        self.doc_span_index = doc_span_index
        self.tokens = tokens
        self.token_to_orig_map = token_to_orig_map
        self.token_is_max_context = token_is_max_context
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.start_position = start_position
        self.end_position = end_position


def read_many_examples(input_file, is_training):
    '''who was the american in space ?	in space'''
    lines_list = span_utils.read_cols_lines(input_file=input_file)
    examples = []
    for i in range(len(lines_list)):
        paragraph_text = lines_list[i][0]
        answer_text = lines_list[i][1]
        doc_tokens = []
        char_to_word_offset = []
        prev_is_whitespace = True
        for c in paragraph_text:
            if span_utils.is_whitespace(c):
                prev_is_whitespace = True
            else:
                if prev_is_whitespace:
                    doc_tokens.append(c)
                else:
                    doc_tokens[-1] += c
                prev_is_whitespace = False
            char_to_word_offset.append(len(doc_tokens) - 1)

        if is_training:
            qas_id = 'train_' + str(i)
        else:
            qas_id = 'test_' + str(i)

        # question_text = 'abc'  #no use
        start_position = None
        end_position = None
        orig_answer_text = None
        if is_training:
            # if len(answer_text) != 1:
            #     raise ValueError("For training, each question should have exactly 1 answer.")
            orig_answer_text = answer_text
            answer_offset = paragraph_text.find(answer_text)  # answer_start
            answer_length = len(orig_answer_text)
            start_position = char_to_word_offset[answer_offset]
            print(paragraph_text, '\t', answer_text)
            end_position = char_to_word_offset[answer_offset + answer_length - 1]
            # Only add answers where the text can be exactly recovered from the
            # document. If this CAN'T happen it's likely due to weird Unicode
            # stuff so we will just skip the example.
            #
            # Note that this means for training mode, every example is NOT
            # guaranteed to be preserved.
            actual_text = " ".join(doc_tokens[start_position:(end_position + 1)])
            cleaned_answer_text = " ".join(whitespace_tokenize(orig_answer_text))
            if actual_text.find(cleaned_answer_text) == -1:
                continue
        else:
            orig_answer_text = answer_text
        example = SequenceExample(
            qas_id=qas_id,
            doc_tokens=doc_tokens,
            orig_answer_text=orig_answer_text,
            start_position=start_position,
            end_position=end_position)
        examples.append(example)
    return examples


def read_one_example(one_line):
    paragraph_text = one_line
    doc_tokens = []
    char_to_word_offset = []
    prev_is_whitespace = True
    for c in paragraph_text:
        if span_utils.is_whitespace(c):
            prev_is_whitespace = True
        else:
            if prev_is_whitespace:
                doc_tokens.append(c)
            else:
                doc_tokens[-1] += c
            prev_is_whitespace = False
        char_to_word_offset.append(len(doc_tokens) - 1)
    # question_text = 'abc'  # no use
    start_position = None
    end_position = None
    orig_answer_text = None
    examples = []
    example = SequenceExample(
            qas_id="test",
            doc_tokens=doc_tokens,
            orig_answer_text=orig_answer_text,
            start_position=start_position,
            end_position=end_position)
    examples.append(example)
    return examples


def convert_examples_to_features(examples, tokenizer, max_seq_length, doc_stride, max_query_length, is_training):
    """Loads a data file into a list of `InputBatch`s."""
    unique_id = 1000000000
    features = []
    for (example_index, example) in enumerate(examples):
        tok_to_orig_index = []  #token - orig word index
        orig_to_tok_index = []  #orig word - token index
        all_doc_tokens = []   #all tokens
        for (i, token) in enumerate(example.doc_tokens):
            orig_to_tok_index.append(len(all_doc_tokens))
            sub_tokens = tokenizer.tokenize(token)
            for sub_token in sub_tokens:
                tok_to_orig_index.append(i)
                all_doc_tokens.append(sub_token)

        tok_start_position = None
        tok_end_position = None
        if is_training:
            tok_start_position = orig_to_tok_index[example.start_position]
            if example.end_position < len(example.doc_tokens) - 1:
                tok_end_position = orig_to_tok_index[example.end_position + 1] - 1
            else:
                tok_end_position = len(all_doc_tokens) - 1
            (tok_start_position, tok_end_position) = span_utils._improve_answer_span(
                all_doc_tokens, tok_start_position, tok_end_position, tokenizer, example.orig_answer_text)

        # The -3 accounts for [CLS], [SEP] and [SEP]
        # max_tokens_for_doc = max_seq_length - len(query_tokens) - 3
        max_tokens_for_doc = max_seq_length - 0 - 3

        # We can have documents that are longer than the maximum sequence length.
        # To deal with this we do a sliding window approach, where we take chunks
        # of the up to our max length with a stride of `doc_stride`.
        # pylint: disable=invalid-name
        _DocSpan = collections.namedtuple("DocSpan", ["start", "length"])
        doc_spans = []
        start_offset = 0
        while start_offset < len(all_doc_tokens):
            length = len(all_doc_tokens) - start_offset
            if length > max_tokens_for_doc:
                length = max_tokens_for_doc
            doc_spans.append(_DocSpan(start=start_offset, length=length))
            if start_offset + length == len(all_doc_tokens):
                break
            start_offset += min(length, doc_stride)

        for (doc_span_index, doc_span) in enumerate(doc_spans):
            tokens = []
            token_to_orig_map = {}
            token_is_max_context = {}
            segment_ids = []
            tokens.append("[CLS]")
            segment_ids.append(1)
            for i in range(doc_span.length):
                split_token_index = doc_span.start + i  #split start
                token_to_orig_map[len(tokens)] = tok_to_orig_index[split_token_index]
                is_max_context = span_utils._check_is_max_context(doc_spans, doc_span_index, split_token_index)
                token_is_max_context[len(tokens)] = is_max_context
                tokens.append(all_doc_tokens[split_token_index])
                segment_ids.append(1)
            tokens.append("[SEP]")
            segment_ids.append(1)

            input_ids = tokenizer.convert_tokens_to_ids(tokens)
            # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
            input_mask = [1] * len(input_ids)

            # Zero-pad up to the sequence length.
            while len(input_ids) < max_seq_length:
                input_ids.append(0)
                input_mask.append(0)
                segment_ids.append(0)

            assert len(input_ids) == max_seq_length
            assert len(input_mask) == max_seq_length
            assert len(segment_ids) == max_seq_length

            start_position = None
            end_position = None
            if is_training:
                # For training, if our document chunk does not contain an annotation
                # we throw it out, since there is nothing to predict.
                doc_start = doc_span.start
                doc_end = doc_span.start + doc_span.length - 1
                if (example.start_position < doc_start or example.end_position < doc_start or
                        example.start_position > doc_end or example.end_position > doc_end):
                    continue
                # doc_offset = len(query_tokens) + 2
                doc_offset = 1
                start_position = tok_start_position - doc_start + doc_offset
                end_position = tok_end_position - doc_start + doc_offset
            # print('#############', tokens)
            # print('#############', tokens_pos)
            # print('#############', input_ids)
            # print('#############', input_pos_ids)
            features.append(
                InputFeatures(
                    unique_id=unique_id,
                    example_index=example_index,
                    doc_span_index=doc_span_index,
                    tokens=tokens,
                    token_to_orig_map=token_to_orig_map,
                    token_is_max_context=token_is_max_context,
                    input_ids=input_ids,
                    input_mask=input_mask,
                    segment_ids=segment_ids,
                    start_position=start_position,
                    end_position=end_position))
            unique_id += 1
    return features


def write_predictions(all_examples, all_features, all_results, n_best_size, max_answer_length, do_lower_case, verbose_logging):
    """Write final predictions to the json file."""
    example_index_to_features = collections.defaultdict(list)
    for feature in all_features:
        example_index_to_features[feature.example_index].append(feature)

    unique_id_to_result = {}
    for result in all_results:
        unique_id_to_result[result.unique_id] = result

    # pylint: disable=invalid-name
    _PrelimPrediction = collections.namedtuple("PrelimPrediction", ["feature_index", "start_index", "start_logit", "end_index", "end_logit"])

    all_predictions = collections.OrderedDict()
    all_nbest_json = collections.OrderedDict()
    eval_accuracy = 0
    instance_num = 0
    for (example_index, example) in enumerate(all_examples):
        features = example_index_to_features[example_index]
        correct_span = example.orig_answer_text
        prelim_predictions = []
        for (feature_index, feature) in enumerate(features):
            if feature.unique_id not in unique_id_to_result.keys(): continue
            result = unique_id_to_result[feature.unique_id]
            start_indexes = span_utils._get_best_indexes(result.start_logits, n_best_size)
            end_indexes = span_utils._get_best_indexes(result.end_logits, n_best_size)

            for start_index in start_indexes:
                for end_index in end_indexes:
                    # We could hypothetically create invalid predictions, e.g., predict
                    # that the start of the span is in the question. We throw out all
                    # invalid predictions.
                    if start_index >= len(feature.tokens):
                        continue
                    if end_index >= len(feature.tokens):
                        continue
                    if start_index not in feature.token_to_orig_map:
                        continue
                    if end_index not in feature.token_to_orig_map:
                        continue
                    if not feature.token_is_max_context.get(start_index, False):
                        continue
                    if end_index < start_index:
                        continue
                    length = end_index - start_index + 1
                    if length > max_answer_length:
                        continue
                    if length == 1:
                        continue
                    prelim_predictions.append(
                        _PrelimPrediction(
                            feature_index=feature_index,
                            start_index=start_index,
                            end_index=end_index,
                            start_logit=result.start_logits[start_index],
                            end_logit=result.end_logits[end_index]))
        prelim_predictions = sorted(prelim_predictions, key=lambda x: (x.start_logit + x.end_logit), reverse=True)

        # pylint: disable=invalid-name
        _NbestPrediction = collections.namedtuple( "NbestPrediction", ["text", "start_logit", "end_logit"])

        seen_predictions = {}
        nbest = []
        for pred in prelim_predictions:
            if len(nbest) >= n_best_size:
                break
            feature = features[pred.feature_index]

            tok_tokens = feature.tokens[pred.start_index:(pred.end_index + 1)]
            orig_doc_start = feature.token_to_orig_map[pred.start_index]
            orig_doc_end = feature.token_to_orig_map[pred.end_index]
            orig_tokens = example.doc_tokens[orig_doc_start:(orig_doc_end + 1)]
            tok_text = " ".join(tok_tokens)

            # De-tokenize WordPieces that have been split off.
            tok_text = tok_text.replace(" ##", "")
            tok_text = tok_text.replace("##", "")

            # Clean whitespace
            tok_text = tok_text.strip()
            tok_text = " ".join(tok_text.split())
            orig_text = " ".join(orig_tokens)

            final_text = span_utils.get_final_text(tok_text, orig_text, do_lower_case, verbose_logging)
            if final_text in seen_predictions:
                continue

            seen_predictions[final_text] = True
            nbest.append(
                _NbestPrediction(
                    text=final_text,
                    start_logit=pred.start_logit,
                    end_logit=pred.end_logit))

        # In very rare edge cases we could have no valid predictions. So we
        # just create a nonce prediction in this case to avoid failure.
        if not nbest:
            nbest.append(_NbestPrediction(text="empty", start_logit=0.0, end_logit=0.0))
        assert len(nbest) >= 1
        total_scores = []
        for entry in nbest:
            total_scores.append(entry.start_logit + entry.end_logit)
        probs = span_utils._compute_softmax(total_scores)
        nbest_json = []
        for (i, entry) in enumerate(nbest):
            output = collections.OrderedDict()
            output["text"] = entry.text
            output["probability"] = probs[i]
            output["start_logit"] = entry.start_logit
            output["end_logit"] = entry.end_logit
            if entry.text == correct_span:
                output["accuracy"] = 1
            else:
                output["accuracy"] = 0
            nbest_json.append(output)

        assert len(nbest_json) >= 1
        all_predictions[example.qas_id] = (nbest_json[0]["text"], nbest_json[0]["accuracy"])
        eval_accuracy += nbest_json[0]["accuracy"]
        instance_num += 1
        all_nbest_json[example.qas_id] = nbest_json

    return eval_accuracy/instance_num, instance_num, all_predictions


def write_span_headwords_with_nbest(all_examples, all_features, all_results, n_best_size, max_answer_length, do_lower_case, verbose_logging):
    '''get span, headwords ,and nbest'''
    span = None
    example_index_to_features = collections.defaultdict(list)
    for feature in all_features:
        example_index_to_features[feature.example_index].append(feature)

    unique_id_to_result = {}
    for result in all_results:
        unique_id_to_result[result.unique_id] = result

    # pylint: disable=invalid-name
    _PrelimPrediction = collections.namedtuple(
        "PrelimPrediction", ["feature_index", "start_index", "end_index", "start_logit", "end_logit"])

    for (example_index, example) in enumerate(all_examples):
        features = example_index_to_features[example_index]

        prelim_predictions = []
        for (feature_index, feature) in enumerate(features):
            result = unique_id_to_result[feature.unique_id]

            start_indexes = span_utils._get_best_indexes(result.start_logits, n_best_size)
            end_indexes = span_utils._get_best_indexes(result.end_logits, n_best_size)
            for start_index in start_indexes:
                for end_index in end_indexes:
                    # We could hypothetically create invalid predictions, e.g., predict
                    # that the start of the span is in the question. We throw out all invalid predictions.
                    if start_index >= len(feature.tokens):
                        continue
                    if end_index >= len(feature.tokens):
                        continue
                    if start_index not in feature.token_to_orig_map:
                        continue
                    if end_index not in feature.token_to_orig_map:
                        continue
                    if not feature.token_is_max_context.get(start_index, False):
                        continue
                    if end_index < start_index:
                        continue
                    length = end_index - start_index + 1
                    if length > max_answer_length:
                        continue

                    if length == 1:
                        continue

                    prelim_predictions.append(
                            _PrelimPrediction(
                                feature_index=feature_index,
                                start_index=start_index,
                                end_index=end_index,
                                start_logit=result.start_logits[start_index],
                                end_logit=result.end_logits[end_index]))

        prelim_predictions = sorted(prelim_predictions, key=lambda x: (x.start_logit + x.end_logit), reverse=True)
        # pylint: disable=invalid-name
        _NbestPrediction = collections.namedtuple("NbestPrediction", ["text", "start_logit", "end_logit"])
        seen_predictions = {}
        nbest = []
        for pred in prelim_predictions:
            if len(nbest) >= n_best_size:
                break
            feature = features[pred.feature_index]

            tok_tokens = feature.tokens[pred.start_index:(pred.end_index + 1)]
            orig_doc_start = feature.token_to_orig_map[pred.start_index]
            orig_doc_end = feature.token_to_orig_map[pred.end_index]
            orig_tokens = example.doc_tokens[orig_doc_start:(orig_doc_end + 1)]
            tok_text = " ".join(tok_tokens)

            # De-tokenize WordPieces that have been split off.
            tok_text = tok_text.replace(" ##", "")
            tok_text = tok_text.replace("##", "")

            # Clean whitespace
            tok_text = tok_text.strip()
            tok_text = " ".join(tok_text.split())
            orig_text = " ".join(orig_tokens)

            final_text = span_utils.get_final_text(tok_text, orig_text, do_lower_case, verbose_logging)
            if final_text in seen_predictions:
                continue

            seen_predictions[final_text] = True
            nbest.append(
                _NbestPrediction(
                    text=final_text,
                    start_logit=pred.start_logit,
                    end_logit=pred.end_logit))

        # In very rare edge cases we could have no valid predictions. So we
        # just create a nonce prediction in this case to avoid failure.
        if not nbest:
            nbest.append(_NbestPrediction(text="empty", start_logit=0.0, end_logit=0.0))
        assert len(nbest) >= 1
        total_scores = []
        for entry in nbest:
            total_scores.append(entry.start_logit + entry.end_logit)
        probs = span_utils._compute_softmax(total_scores)
        nbest_json = []
        for (i, entry) in enumerate(nbest):
            output = collections.OrderedDict()
            output["text"] = entry.text
            output["probability"] = probs[i]
            output["start_logit"] = entry.start_logit
            output["end_logit"] = entry.end_logit
            nbest_json.append(output)
        assert len(nbest_json) >= 1
        span = nbest_json[0]["text"]
    return span


RawResult = collections.namedtuple("RawResult", ["unique_id", "start_logits", "end_logits"])


def main(args=None):
    if args is None:
        args = model_utils.run_redundancy_span_get_local_args()
    if args.local_rank == -1 or args.no_cuda:
        device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
        n_gpu = torch.cuda.device_count()
    else:
        torch.cuda.set_device(args.local_rank)
        device = torch.device("cuda", args.local_rank)
        n_gpu = 1
        # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
        torch.distributed.init_process_group(backend='nccl')
    # logger.info("device: {} n_gpu: {}, distributed training: {}, 16-bits training: {}".format(
    #     device, n_gpu, bool(args.local_rank != -1), args.fp16))
    if args.gradient_accumulation_steps < 1:
        raise ValueError("Invalid gradient_accumulation_steps parameter: {}, should be >= 1".format(args.gradient_accumulation_steps))
    args.train_batch_size = int(args.train_batch_size / args.gradient_accumulation_steps)

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(args.seed)

    if not args.do_train and not args.do_predict:
        raise ValueError("At least one of `do_train` or `do_predict` must be True.")
    if args.do_train:
        if not args.train_file:
            raise ValueError("If `do_train` is True, then `train_file` must be specified.")
    if args.do_predict:
        if not args.predict_file:
            raise ValueError("If `do_predict` is True, then `predict_file` must be specified.")
    if os.path.exists(args.output_dir) and os.listdir(args.output_dir):
        raise ValueError("Output directory () already exists and is not empty.")
    os.makedirs(args.output_dir, exist_ok=True)

    tokenizer = BertTokenizer.from_pretrained(args.bert_model)

    train_examples = None
    num_train_steps = None
    if args.do_train:
        train_examples = read_many_examples(input_file=args.train_file, is_training=True)
        num_train_steps = int(len(train_examples) / args.train_batch_size / args.gradient_accumulation_steps * args.num_train_epochs)

    # Prepare model
    """=========fine-tune 1==========="""
    model = BertForQuestionAnswering.from_pretrained(args.bert_model,
                cache_dir=PYTORCH_PRETRAINED_BERT_CACHE / 'distributed_{}'.format(args.local_rank))
    print (PYTORCH_PRETRAINED_BERT_CACHE / 'distributed_{}'.format(args.local_rank))
    if args.fp16:
        model.half()
    model.to(device)
    """=============================="""

    if args.local_rank != -1:
        try:
            from apex.parallel import DistributedDataParallel as DDP
        except ImportError:
            raise ImportError("Please install apex from https://www.github.com/nvidia/apex to use distributed and fp16 training.")
        model = DDP(model)
    elif n_gpu > 1:
        model = torch.nn.DataParallel(model)

    # Prepare optimizer
    param_optimizer = list(model.named_parameters())

    # hack to remove pooler, which is not used
    # thus it produce None grad that break apex
    param_optimizer = [n for n in param_optimizer if 'pooler' not in n[0]]

    no_decay = ['bias', 'LayerNorm.bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': 0.01},
        {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}]

    t_total = num_train_steps
    if args.local_rank != -1:
        t_total = t_total // torch.distributed.get_world_size()
    if args.fp16:
        try:
            from apex.optimizers import FP16_Optimizer
            from apex.optimizers import FusedAdam
        except ImportError:
            raise ImportError("Please install apex from https://www.github.com/nvidia/apex to use distributed and fp16 training.")
        optimizer = FusedAdam(optimizer_grouped_parameters,
                              lr=args.learning_rate,
                              bias_correction=False,
                              max_grad_norm=1.0)
        if args.loss_scale == 0:
            optimizer = FP16_Optimizer(optimizer, dynamic_loss_scale=True)
        else:
            optimizer = FP16_Optimizer(optimizer, static_loss_scale=args.loss_scale)
    else:
        optimizer = BertAdam(optimizer_grouped_parameters,
                             lr=args.learning_rate,
                             warmup=args.warmup_proportion,
                             t_total=t_total)

    max_eval_accuracy = 0
    global_step = 0
    if args.do_train:
        cached_train_features_file = args.train_file + '_{0}_{1}_{2}_{3}'.format(
            args.bert_model, str(args.max_seq_length), str(args.doc_stride), str(args.max_query_length))
        train_features = None
        try:
            with open(cached_train_features_file, "rb") as reader:
                train_features = pickle.load(reader)
        except:
            train_features = convert_examples_to_features(
                examples=train_examples,
                tokenizer=tokenizer,
                max_seq_length=args.max_seq_length,
                doc_stride=args.doc_stride,
                max_query_length=args.max_query_length,
                is_training=True)
            if args.local_rank == -1 or torch.distributed.get_rank() == 0:
                # logger.info("  Saving train features into cached file %s", cached_train_features_file)
                with open(cached_train_features_file, "wb") as writer:
                    pickle.dump(train_features, writer)
        all_input_ids = torch.tensor([f.input_ids for f in train_features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in train_features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in train_features], dtype=torch.long)
        all_start_positions = torch.tensor([f.start_position for f in train_features], dtype=torch.long)
        all_end_positions = torch.tensor([f.end_position for f in train_features], dtype=torch.long)

        train_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_start_positions, all_end_positions)
        if args.local_rank == -1:
            train_sampler = RandomSampler(train_data)
        else:
            train_sampler = DistributedSampler(train_data)
        train_dataloader = DataLoader(train_data, sampler=train_sampler, batch_size=args.train_batch_size)

        if args.do_predict and (args.local_rank == -1 or torch.distributed.get_rank() == 0):
            eval_examples = read_many_examples(input_file=args.predict_file, is_training=False)
            eval_features = convert_examples_to_features(
                examples=eval_examples,
                tokenizer=tokenizer,
                max_seq_length=args.max_seq_length,
                doc_stride=args.doc_stride,
                max_query_length=args.max_query_length,
                is_training=False)
            all_input_ids = torch.tensor([f.input_ids for f in eval_features], dtype=torch.long)
            all_input_mask = torch.tensor([f.input_mask for f in eval_features], dtype=torch.long)
            all_segment_ids = torch.tensor([f.segment_ids for f in eval_features], dtype=torch.long)
            # all_start_positions = torch.tensor([f.start_position for f in train_features], dtype=torch.long)
            # all_end_positions = torch.tensor([f.end_position for f in train_features], dtype=torch.long)
            all_example_index = torch.arange(all_input_ids.size(0), dtype=torch.long)
            eval_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_example_index)
            # Run prediction for full data
            eval_sampler = SequentialSampler(eval_data)
            eval_dataloader = DataLoader(eval_data, sampler=eval_sampler, batch_size=args.predict_batch_size)

        for _ in trange(int(args.num_train_epochs), desc="Epoch"):
            model.train()
            for step, batch in enumerate(tqdm(train_dataloader, desc="Iteration")):
                if n_gpu == 1:
                    batch = tuple(t.to(device) for t in batch)  # multi-gpu does scattering it-self
                input_ids, input_mask, segment_ids, start_positions, end_positions = batch
                loss = model(input_ids=input_ids, token_type_ids=segment_ids,
                      attention_mask=input_mask, start_positions=start_positions, end_positions=end_positions)
                if n_gpu > 1:
                    loss = loss.mean()  # mean() to average on multi-gpu.
                if args.gradient_accumulation_steps > 1:
                    loss = loss / args.gradient_accumulation_steps

                if args.fp16:
                    optimizer.backward(loss)
                else:
                    loss.backward(retain_graph=True)
                if (step + 1) % args.gradient_accumulation_steps == 0:
                    # modify learning rate with special warm up BERT uses
                    lr_this_step = args.learning_rate * span_utils.warmup_linear(global_step / t_total, args.warmup_proportion)
                    for param_group in optimizer.param_groups:
                        param_group['lr'] = lr_this_step
                    optimizer.step()
                    optimizer.zero_grad()
                    global_step += 1

            if args.do_predict and (args.local_rank == -1 or torch.distributed.get_rank() == 0):
                model.eval()
                all_results = []
                # logger.info("Start evaluating")
                for input_ids, input_mask, segment_ids, example_indices, in tqdm(eval_dataloader, desc="Evaluating"):
                    # if len(all_results) % 1000 == 0: logger.info("Processing example: %d" % (len(all_results)))

                    input_ids = input_ids.to(device)
                    input_mask = input_mask.to(device)
                    segment_ids = segment_ids.to(device)

                    with torch.no_grad():
                        batch_start_logits, batch_end_logits = model(input_ids=input_ids, token_type_ids=segment_ids, attention_mask=input_mask)

                    for i, example_index in enumerate(example_indices):
                        start_logits = batch_start_logits[i].detach().cpu().tolist()
                        end_logits = batch_end_logits[i].detach().cpu().tolist()
                        eval_feature = eval_features[example_index.item()]
                        # unique_id = int(eval_feature.unique_id)
                        all_results.append(RawResult(unique_id=int(eval_feature.unique_id), start_logits=start_logits, end_logits=end_logits))

                eval_accuracy,instance_num, all_predictions = write_predictions(eval_examples, eval_features,
                                                                                all_results, args.n_best_size, args.max_answer_length,
                                                                                args.do_lower_case, args.verbose_logging)
                if max_eval_accuracy < eval_accuracy:
                    max_eval_accuracy = eval_accuracy
                    # Save a trained model
                    model_to_save = model.module if hasattr(model, 'module') else model  # Only save the model it-self
                    output_model_file = os.path.join(args.output_dir, "pytorch_model.bin")
                    torch.save(model_to_save.state_dict(), output_model_file)
                    output_prediction_file = os.path.join(args.output_dir, "predictions.json")
                    output_nbest_file = os.path.join(args.output_dir, "nbest_predictions.json")
                    with open(output_prediction_file, "w") as writer:
                        writer.write(json.dumps(all_predictions, indent=4) + "\n")
                    # with open(output_nbest_file, "w") as writer:
                    #     writer.write(json.dumps(all_nbest_json, indent=4) + "\n")
                    result_json = collections.OrderedDict()
                    result_json['result'] = eval_accuracy
                    result_json['eval_accuracy'] = eval_accuracy
                    result_json['instance_num'] = instance_num
                    with open(output_nbest_file, "w") as writer:
                        writer.write(json.dumps(result_json, indent=4) + "\n")


if __name__ == "__main__":
    main()
