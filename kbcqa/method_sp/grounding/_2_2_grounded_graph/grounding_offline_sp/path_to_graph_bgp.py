import collections
from common_structs.grounded_graph import GroundedNode, GroundedEdge
from method_sp.grounding import grounding_args


def parser_composition_q_freebase_ir(data_dict, s1=None,t1=None):
    candidate_graphquery_list = []
    for querytype in data_dict:
        if querytype == "1_0":
            candidate_graphquery_list.extend(_1_0_to_graphs(data_dict['1_0'], s1=s1, t1=t1))
        elif querytype == "1_1":
            candidate_graphquery_list.extend(_1_1_to_graphs(data_dict['1_1'], s1=s1, t1=t1))
        elif querytype == "1_2":
            candidate_graphquery_list.extend(_1_2_to_graphs(data_dict['1_2'], s1=s1, t1=t1))
        elif querytype == "1_2_2":
            candidate_graphquery_list.extend(_1_2_to_graphs(data_dict['1_2_2'], s1=s1, t1=t1))
        elif querytype == "1_3":
            candidate_graphquery_list.extend(_1_3_to_graphs(data_dict['1_3'], s1=s1, t1=t1))
    return candidate_graphquery_list


def parser_composition_q_freebase_sp(data_dict, s1=None,t1=None, is_constraint_mediator=False):
    candidate_graphquery_list = []
    for querytype in data_dict:
        if querytype == "1_0" and is_constraint_mediator:
            candidate_graphquery_list.extend(_1_0_to_graphs(data_dict['1_0'],s1=s1, t1=t1))
        elif querytype == "1_1":
            # composition-0 mediator; composition-1  no mediator
            candidate_graphquery_list.extend(_1_1_to_graphs(data_dict['1_1'], s1=s1, t1=t1, need_mediator=is_constraint_mediator))
        elif querytype == "1_2" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_2_to_graphs(data_dict['1_2'], s1=s1, t1=t1))
        elif querytype == "1_2_2" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_2_to_graphs(data_dict['1_2_2'], s1=s1, t1=t1))
        elif querytype == "1_3" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_3_to_graphs(data_dict['1_3'], s1=s1, t1=t1))
        # else:
        #     print ('Other structure', querytype)
    return candidate_graphquery_list


def parser_conjunction_q_freebase(data_dict, s1=None, s2=None, t1=None,t2=None):
    candidate_graphquery_list = []
    for querytype in data_dict:
        if querytype == "2_0":
            candidate_graphquery_list.extend(_2_0_to_graphs(data_dict['2_0'], s1=s1, s2=s2, t1=t1, t2=t2))
        elif querytype == "2_1":
            candidate_graphquery_list.extend(_2_1_to_graphs(data_dict['2_1'], s1=s1, s2=s2, t1=t1, t2=t2))
        elif querytype == "2_2":
            candidate_graphquery_list.extend(_2_2_to_graphs(data_dict['2_2'], s1=s1, s2=s2, t1=t1, t2=t2))
        elif querytype == "2_3":
            candidate_graphquery_list.extend(_2_3_to_graphs(data_dict['2_3'], s1=s1, s2=s2,t1=t1,t2=t2))
        else:
            print ('Other structure', querytype)
    return candidate_graphquery_list


def parser_composition_q_dbpedia_ir(data_dict, s1=None,t1=None):
    candidate_graphquery_list = []
    for querytype in data_dict:
        # 1_0
        if querytype == "1_0":
            candidate_graphquery_list.extend(_1_0_to_graphs(data_dict['1_0'], s1=s1, t1=t1))
        elif querytype == "1_0_b":
            candidate_graphquery_list.extend(_1_0_b_to_graphs(data_dict['1_0_b'], s1=s1, t1=t1))
        # 1_1
        elif querytype == "1_1":
            candidate_graphquery_list.extend(_1_1_to_graphs(data_dict['1_1'], s1=s1, t1=t1))
        elif querytype == "1_1_b":
            candidate_graphquery_list.extend(_1_1_b_to_graphs(data_dict['1_1_b'], s1=s1, t1=t1))
        elif querytype == "1_1_c":
            candidate_graphquery_list.extend(_1_1_c_to_graphs(data_dict['1_1_c'], s1=s1, t1=t1))
        elif querytype == "1_1_d":
            candidate_graphquery_list.extend(_1_1_d_to_graphs(data_dict['1_1_d'], s1=s1, t1=t1))
        # else:
        #     print ('Other structure', querytype)
    return candidate_graphquery_list


def parser_composition_q_dbpedia_sp(data_dict, s1=None,t1=None, is_constraint_mediator=False):
    candidate_graphquery_list = []
    for querytype in data_dict:
        #1_0
        if querytype == "1_0" and is_constraint_mediator:
            candidate_graphquery_list.extend(_1_0_to_graphs(data_dict['1_0'],s1=s1,t1=t1))
        elif querytype == "1_0_b" and is_constraint_mediator:
            candidate_graphquery_list.extend(_1_0_b_to_graphs(data_dict['1_0_b'],s1=s1,t1=t1))
        #1_1
        elif querytype == "1_1" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_1_to_graphs(data_dict['1_1'],s1=s1,t1=t1))
        elif querytype == "1_1_b" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_1_b_to_graphs(data_dict['1_1_b'],s1=s1,t1=t1))
        elif querytype == "1_1_c" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_1_c_to_graphs(data_dict['1_1_c'],s1=s1,t1=t1))
        elif querytype == "1_1_d" and not is_constraint_mediator:
            candidate_graphquery_list.extend(_1_1_d_to_graphs(data_dict['1_1_d'],s1=s1,t1=t1))
    return candidate_graphquery_list


def parser_conjunction_q_dbpedia(data_dict, s1=None, s2=None,t1=None,t2=None):
    candidate_graphquery_list = []
    for querytype in data_dict:
        if querytype == "2_0":
            candidate_graphquery_list.extend(_2_0_to_graphs(data_dict['2_0'], s1=s1, s2=s2,t1=t1,t2=t2))
        elif querytype == "2_0_b":
            candidate_graphquery_list.extend(_2_0_b_to_graphs(data_dict['2_0_b'], s1=s1, s2=s2,t1=t1,t2=t2))
        elif querytype == "2_0_c":
            candidate_graphquery_list.extend(_2_0_c_to_graphs(data_dict['2_0_c'], s1=s1, s2=s2,t1=t1,t2=t2))
        elif querytype == "2_0_d":
            candidate_graphquery_list.extend(_2_0_d_to_graphs(data_dict['2_0_d'], s1=s1, s2=s2,t1=t1,t2=t2))
    return candidate_graphquery_list


def parser_yesno_q_dbpedia(data_dict, s1=None, s2=None, t1=None, t2=None):
    candidate_graphquery_list = []
    for querytype in data_dict:
        if querytype == "3_0":
            candidate_graphquery_list.extend(_3_0_to_graphs(data_dict['3_0'], s1=s1, s2=s2, t1=t1, t2=t2))
        elif querytype == "3_0_b":
            candidate_graphquery_list.extend(_3_0_b_to_graphs(data_dict['3_0_b'], s1=s1, s2=s2, t1=t1, t2=t2))
        # else:
        #     print ('Other structure', querytype)
    return candidate_graphquery_list


def _1_0_to_graphs(candidate_pathes, s1, t1):
    '''1_0 	entity-{p}->o	对应, 第1位对应到路径是p, 第二位对应到路径是o
    ns:m.0dhqrm "organization.organization.headquarters\tm.08cshk7'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid+=1
    node_answer_entity= GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p_answers=collections.defaultdict(set)
    for candidate in candidate_pathes:
        cols = candidate.split("\t")
        if len(cols) != 2:
            continue
        relation, answer_entity = cols
        p_answers[relation].add(answer_entity)

    for p in p_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_0'
        candidate_graphquery["nodes"] = [node_topic_entity, node_answer_entity]

        if t1=='literal': #如果是literal就翻一番
            edge=GroundedEdge(start=node_answer_entity.nid,end=node_topic_entity.nid,relation=p)
        else:
            edge = GroundedEdge(start=node_topic_entity.nid, end=node_answer_entity.nid, relation=p)

        candidate_graphquery["edges"] = [edge]
        candidate_graphquery["path"] = p
        candidate_graphquery["denotation"] = list(p_answers[p])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_0_b_to_graphs(candidate_pathes, s1, t1):
    '''
    s-{p}->entity
     "http://dbpedia.org/resource/Vivian_Kubrick\thttp://dbpedia.org/ontology/parent"  entity	//两个对应,  第1位对应到路径是s, 第二位对应到路径是p.
    :param candidate_pathes:
    :param s1:
    :param t1:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p_answers = collections.defaultdict(set)
    for candidate in candidate_pathes:
        cols = candidate.split("\t")
        if len(cols) != 2:
            continue
        answer_entity, relation = cols
        p_answers[relation].add(answer_entity)
    for p in p_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_0_b'
        candidate_graphquery["nodes"] = [node_topic_entity, node_answer_entity]
        edge = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity.nid, relation=p)
        candidate_graphquery["edges"] = [edge]
        candidate_graphquery["path"] = p
        candidate_graphquery["denotation"] = list(p_answers[p])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_1_to_graphs(paths, s1, t1, need_mediator=False):
    '''
    e-{p1}->c*-{p2}->a
    "organization.organization.headquarters\tm.08cshk7\tlocation.mailing_address.state_province_region\tm.015jr
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 4: continue
        p1, c_entity, p2, answer_entity = cols
        # filter c entity
        # --------------------------------------
        # webq, graphquestions
        if need_mediator: #仅仅考虑mediator
            if c_entity in grounding_args.mediators_instances_set:
                p1_p2_answers['\t'.join([p1,p2])].add(answer_entity)
        else: # 不考虑need mediator, 所有的都考虑, lcquad
            p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)
        # --------------------------------------
    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_1'
        candidate_graphquery["nodes"] = [node_topic_entity, node_c_entity, node_answer_entity]
        p1,p2 = p1_p2.split('\t')
        if t1=='literal':
            edge1 = GroundedEdge(start=node_c_entity.nid, end=node_topic_entity.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity.nid, end=node_c_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_c_entity.nid, end=node_answer_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_1_b_to_graphs(paths, s1,t1):
    '''
    e->c*<-a 完全对应
    Saraban "http://dbpedia.org/property/distributor\thttp://dbpedia.org/resource/Sony_Pictures_Classics\thttp://dbpedia.org/ontology/distributor\thttp://dbpedia.org/resource/Lambert_&_Stamp"
    :param paths:
    :param s1:
    :param t1:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)

    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 4:
            continue
        p1, c_entity, p2, answer_entity = cols #完全对应
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)
    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_1_b'
        candidate_graphquery["nodes"] = [node_topic_entity, node_c_entity, node_answer_entity]
        p1,p2 = p1_p2.split('\t')
        edge1 = GroundedEdge(start=node_topic_entity.nid, end=node_c_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_c_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_1_c_to_graphs(paths, s1,t1):
    '''
    e<-{p1}-c*<-{p2}-a
    entity(Stanley_Kubrick) <- "http://dbpedia.org/property/influences\thttp://dbpedia.org/resource/Daniel_Knauf\thttp://dbpedia.org/property/writer\thttp://dbpedia.org/resource/The_Kenyon_Family",
    两个对应, 第1位对应到路径的p1,  第2位对应到路径的c, 第3位对应到路径的p2, 第4位对应路径的a,
    :param paths:
    :param s1:
    :param t1:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 4:
            continue
        p1, c_entity, p2, answer_entity = cols
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_1_c'
        candidate_graphquery["nodes"] = [node_topic_entity, node_c_entity, node_answer_entity]
        p1, p2 = p1_p2.split('\t')
        edge1 = GroundedEdge(start=node_c_entity.nid, end=node_topic_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_c_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_1_d_to_graphs(paths, s1,t1):
    '''
    e<-{p1}-c*-{p2}->a
    entity(Stanley_Kubrick) <- "http://dbpedia.org/ontology/director \t http://dbpedia.org/resource/Fear_and_Desire \t http://dbpedia.org/ontology/producer \t http://dbpedia.org/resource/ Stanley_Kubrick"
    两个对应,
    :param paths:
    :param s1:
    :param t1:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 4:
            continue
        p1, c_entity, p2, answer_entity = cols
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_1_d'
        candidate_graphquery["nodes"] = [node_topic_entity, node_c_entity, node_answer_entity]
        p1,p2 = p1_p2.split('\t')
        edge1 = GroundedEdge(start=node_c_entity.nid, end=node_topic_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_c_entity.nid, end=node_answer_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1,edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_2_to_graphs(paths, s1,t1):
    '''
    #e-{p1}->*1-{p2}->*2-{p3}->a 对应
    Saraband -> "http://dbpedia.org/property/starring\thttp://dbpedia.org/resource/Erland_Josephson\thttp://dbpedia.org/property/spouse\thttp://dbpedia.org/resource/Kristina_Adolphson\thttp://dbpedia.org/property/birthDate\t1937-09-02",
    :param paths:
    :param s1:
    :param t1:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m_entity = GroundedNode(nid=current_nid, node_type="class", id='?m', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_p3_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split('\t')
        if len(cols) != 6:
            continue
        p1, m_entity, p2, c_entity, p3, answer_entity = candidate.split("\t")
        p1_p2_p3_answers['\t'.join([p1, p2, p3])].add(answer_entity)

    for p1_p2_p3 in p1_p2_p3_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_2'
        candidate_graphquery["nodes"] = [node_topic_entity,node_m_entity, node_c_entity, node_answer_entity]
        p1, p2,p3 = p1_p2_p3.split('\t')
        if t1=='literal':
            edge1 = GroundedEdge(start=node_m_entity.nid, end=node_topic_entity.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity.nid, end=node_m_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_m_entity.nid, end=node_c_entity.nid, relation=p2)
        edge3 = GroundedEdge(start=node_c_entity.nid, end=node_answer_entity.nid, relation=p3)
        candidate_graphquery["edges"] = [edge1, edge2, edge3]
        candidate_graphquery["path"] = p1_p2_p3
        candidate_graphquery["denotation"] = list(p1_p2_p3_answers[p1_p2_p3])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _1_3_to_graphs(paths, s1, t1):
    '''
    2020.06.07
        #e-{p1}->m1-{p2}->o1-{p3}->m2->{p4}->o2 对应
        :param paths:
        :param s1:
        :param t1:
        :return:
        '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m_entity = GroundedNode(nid=current_nid, node_type="class", id='?m', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_c_entity = GroundedNode(nid=current_nid, node_type="class", id='?c', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_k_entity = GroundedNode(nid=current_nid, node_type="class", id='?k', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)

    p1_p2_p3_p4_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split('\t')
        if len(cols) != 8:
            continue
        # e - {p1}->m1 - {p2}->o1 - {p3}->m2->{p4}->o2
        p1, m_1_entity, p2, o1_entity, p3, m_2_entity, p4, answer_entity = candidate.split("\t")
        p1_p2_p3_p4_answers['\t'.join([p1, p2, p3, p4])].add(answer_entity)

    for p1_p2_p3_p4 in p1_p2_p3_p4_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '1_3'
        candidate_graphquery["nodes"] = [node_topic_entity, node_m_entity, node_c_entity, node_k_entity, node_answer_entity]
        p1, p2, p3, p4 = p1_p2_p3_p4.split('\t')
        if t1 == 'literal':
            edge1 = GroundedEdge(start=node_m_entity.nid, end=node_topic_entity.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity.nid, end=node_m_entity.nid, relation=p1)
        edge2 = GroundedEdge(start=node_m_entity.nid, end=node_c_entity.nid, relation=p2)
        edge3 = GroundedEdge(start=node_c_entity.nid, end=node_k_entity.nid, relation=p3)
        edge4 = GroundedEdge(start=node_k_entity.nid, end=node_answer_entity.nid, relation=p4)
        candidate_graphquery["edges"] = [edge1, edge2, edge3, edge4]
        candidate_graphquery["path"] = p1_p2_p3_p4
        candidate_graphquery["denotation"] = list(p1_p2_p3_p4_answers[p1_p2_p3_p4])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_0_to_graphs(paths, s1, s2, t1, t2):
    '''
    	e1->a<-e2
    	【对应】	比如:	Google_Videos	"http://dbpedia.org/ontology/owner\thttp://dbpedia.org/resource/Google\thttp://dbpedia.org/ontology/author"		Google_Web_Toolkit
    :param paths:
    :param s1:
    :param s2:
    :param t1:
    :param t2:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:  #merge answers
        p1, answer_entity, p2 = candidate.split("\t")
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_0'
        candidate_graphquery["nodes"] = [node_topic_entity1, node_topic_entity2, node_answer_entity]
        p1, p2 = p1_p2.split('\t')

        if t1=='literal':
            edge1 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity1.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_answer_entity.nid, relation=p1)

        if t2=='literal':
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity2.nid, relation=p2)
        else:
            edge2 = GroundedEdge(start=node_topic_entity2.nid, end=node_answer_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_0_b_to_graphs(paths, s1, s2, t1, t2):
    '''e1<-a->e2
    【对应】	Neil_Brown_(Australian_politician)	 "http://dbpedia.org/property/deputy\thttp://dbpedia.org/resource/John_Howard\thttp://dbpedia.org/property/successor"	Andrew_Peacock'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 3:
            continue
        p1, answer_entity, p2 = cols
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_0_b'
        candidate_graphquery["nodes"] = [node_topic_entity1,node_topic_entity2, node_answer_entity]
        p1, p2 = p1_p2.split('\t')
        if t1=='literal':
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_answer_entity.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity1.nid, relation=p1)
        if t2=='literal':
            edge2 = GroundedEdge(start=node_topic_entity2.nid, end=node_answer_entity.nid, relation=p2)
        else:
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity2.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_0_c_to_graphs(paths, s1, s2, t1, t2):
    '''e1->a->e2'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 3:
            continue
        p1, answer_entity, p2 = cols
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_0_c'
        candidate_graphquery["nodes"] = [node_topic_entity1,node_topic_entity2, node_answer_entity]
        p1, p2 = p1_p2.split('\t')
        if t1=='literal':
            edge1 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity1.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_answer_entity.nid, relation=p1)
        if t2=='literal':
            edge2 = GroundedEdge(start=node_topic_entity2.nid, end=node_answer_entity.nid, relation=p2)
        else:
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity2.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_0_d_to_graphs(paths, s1, s2, t1, t2):
    '''
    	e1<-a<-e2
    	【对应】	Joe_Pass	http://dbpedia.org/ontology/associatedMusicalArtist\thttp://dbpedia.org/resource/Norman_Granz\thttp://dbpedia.org/ontology/producer",	Dream_Dancing_(album)'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 3:
            continue
        p1, answer_entity, p2 = cols
        p1_p2_answers['\t'.join([p1, p2])].add(answer_entity)

    for p1_p2 in p1_p2_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_0_d'
        candidate_graphquery["nodes"] = [node_topic_entity1,node_topic_entity2, node_answer_entity]
        p1, p2 = p1_p2.split('\t')
        if t1=='literal':
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_answer_entity.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity1.nid, relation=p1)
        if t2=='literal':
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity2.nid, relation=p2)
        else:
            edge2 = GroundedEdge(start=node_topic_entity2.nid, end=node_answer_entity.nid, relation=p2)
        candidate_graphquery["edges"] = [edge1, edge2]
        candidate_graphquery["path"] = p1_p2
        candidate_graphquery["denotation"] = list(p1_p2_answers[p1_p2])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_1_to_graphs(paths, s1, s2,t1,t2):
    '''
    e0-{p1}->*1-{p2}->a<-{p3}-e1
    对应】

    比如: e0{Marine_Corps_Air_Station_Kaneohe_Bay} 	http://dbpedia.org/ontology/city\thttp://dbpedia.org/resource/Marine_Corps_Base_Hawaii\thttp://dbpedia.org/ontology/builder\thttp://dbpedia.org/resource/United_States_Navy\thttp://dbpedia.org/property/operator	e1{New_Sanno_Hotel}'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid +=1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m_entity = GroundedNode(nid=current_nid, node_type="class", id='?m', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_p3_answers = collections.defaultdict(set)
    for candidate in paths:   #merge answers
        p1, m_entity, p2, answer_entity, p3  = candidate.split("\t")
        p1_p2_p3_answers['\t'.join([p1, p2, p3])].add(answer_entity)

    for p1_p2_p3 in p1_p2_p3_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_1'
        candidate_graphquery["nodes"] = [node_topic_entity1, node_topic_entity2, node_m_entity, node_answer_entity]
        p1, p2, p3 = p1_p2_p3.split('\t')

        if t1 == 'literal':
            edge1 = GroundedEdge(start=node_m_entity.nid, end=node_topic_entity1.nid, relation=p1)
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_m_entity.nid, relation=p2)
        else:
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_m_entity.nid, relation=p1)
            edge2 = GroundedEdge(start=node_m_entity.nid, end=node_answer_entity.nid, relation=p2)
        # edge2=GroundedEdge(start=node_m_entity.nid, end=node_answer_entity.nid, relation=p2)
        if t2 == 'literal':
            edge3 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity2.nid, relation=p3)
        else:
            edge3 = GroundedEdge(start=node_topic_entity2.nid, end=node_answer_entity.nid, relation=p3)

        candidate_graphquery["edges"] = [edge1, edge2, edge3]
        candidate_graphquery["path"] = p1_p2_p3
        candidate_graphquery["denotation"] = list(p1_p2_p3_answers[p1_p2_p3])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_2_to_graphs(paths, s1, s2,t1, t2):
    '''e0-{p1}->a<-{p2}-*1<-{p3}-e1
     e0{Sam_Loyd} http://dbpedia.org/property/birthPlace\thttp://dbpedia.org/resource/United_States\t
        http://dbpedia.org/ontology/birthPlace      \thttp://dbpedia.org/resource/New_York_City         \thttp://dbpedia.org/ontology/country",	e1{Eric_Schiller}
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m_entity = GroundedNode(nid=current_nid, node_type="class", id='?m', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_p3_answers = collections.defaultdict(set)
    for candidate in paths:
        p1, answer_entity, p3, m_entity, p2 = candidate.split("\t")
        p1_p2_p3_answers['\t'.join([p1, p2, p3])].add(answer_entity)
    for p1_p2_p3 in p1_p2_p3_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_2'
        candidate_graphquery["nodes"] = [node_topic_entity1, node_topic_entity2, node_m_entity, node_answer_entity]
        p1, p2, p3 = p1_p2_p3.split('\t')
        if t1 == 'literal':
            edge1 = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity1.nid, relation=p1)
        else:
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_answer_entity.nid, relation=p1)

        # edge2 = GroundedEdge(start=node_m_entity.nid, end=node_answer_entity.nid, relation=p2)
        if t2 == 'literal':
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_m_entity.nid, relation=p2)
            edge3 = GroundedEdge(start=node_m_entity.nid, end=node_topic_entity2.nid, relation=p3)
        else:
            edge2 = GroundedEdge(start=node_m_entity.nid, end=node_answer_entity.nid, relation=p2)
            edge3 = GroundedEdge(start=node_topic_entity2.nid, end=node_m_entity.nid, relation=p3)

        candidate_graphquery["edges"] = [edge1, edge2, edge3]
        candidate_graphquery["path"] = p1_p2_p3
        candidate_graphquery["denotation"] = list(p1_p2_p3_answers[p1_p2_p3])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _2_3_to_graphs(paths, s1, s2,t1,t2):
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity1 = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_topic_entity2 = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m1_entity = GroundedNode(nid=current_nid, node_type="class", id='?m1', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_m2_entity = GroundedNode(nid=current_nid, node_type="class", id='?m2', type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type="class", id='?a', type_class='', friendly_name="", question_node=1)
    p1_p2_p3_p4_answers = collections.defaultdict(set)
    for candidate in paths:  #merge answers
        p1, m1_entity, p2, answer_entity, p4, m2_entity, p3 = candidate.split("\t")
        p1_p2_p3_p4_answers['\t'.join([p1, p2, p3, p4])].add(answer_entity)

    for p1_p2_p3_p4 in p1_p2_p3_p4_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '2_3'
        candidate_graphquery["nodes"] = [node_topic_entity1, node_topic_entity2, node_m1_entity,node_m2_entity, node_answer_entity]
        p1, p2, p3, p4 = p1_p2_p3_p4.split('\t')
        if t1 == 'literal':
            edge1 = GroundedEdge(start=node_m1_entity.nid, end=node_topic_entity1.nid, relation=p1)
            edge2 = GroundedEdge(start=node_answer_entity.nid, end=node_m1_entity.nid, relation=p2)
        else:
            edge1 = GroundedEdge(start=node_topic_entity1.nid, end=node_m1_entity.nid, relation=p1)
            edge2 = GroundedEdge(start=node_m1_entity.nid, end=node_answer_entity.nid, relation=p2)

        if t2 == 'literal':
            edge3 = GroundedEdge(start=node_answer_entity.nid, end=node_m2_entity.nid, relation=p3)
            edge4 = GroundedEdge(start=node_m2_entity.nid, end=node_topic_entity2.nid, relation=p4)
        else:
            edge3 = GroundedEdge(start=node_m2_entity.nid, end=node_answer_entity.nid, relation=p3)
            edge4 = GroundedEdge(start=node_topic_entity2.nid, end=node_m2_entity.nid, relation=p4)

        candidate_graphquery["edges"] = [edge1, edge2, edge3,edge4]
        candidate_graphquery["path"] = p1_p2_p3_p4
        candidate_graphquery["denotation"] = list(p1_p2_p3_p4_answers[p1_p2_p3_p4])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _3_0_to_graphs(paths, s1, s2, t1, t2):
    '''1_0 	entity-{p}->o	对应, 第1位对应到路径是p, 第二位对应到路径是o
        ns:m.0dhqrm "organization.organization.headquarters\tm.08cshk7'''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=1)
    p_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 2:
            continue
        relation, answer_entity = cols
        p_answers[relation].add(answer_entity)

    for p in p_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '3_0'
        candidate_graphquery["nodes"] = [node_topic_entity, node_answer_entity]
        if t1 == 'literal':  # 如果是literal就翻一番
            edge = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity.nid, relation=p)
        else:
            edge = GroundedEdge(start=node_topic_entity.nid, end=node_answer_entity.nid, relation=p)
        candidate_graphquery["edges"] = [edge]
        candidate_graphquery["path"] = p
        candidate_graphquery["denotation"] = list(p_answers[p])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list


def _3_0_b_to_graphs(paths, s1, s2, t1, t2):
    '''
         s p   "http://dbpedia.org/resource/The_Office_(U.S._TV_series)\thttp://dbpedia.org/ontology/executiveProducer",
    :param paths:
    :param s1:
    :param s2:
    :param t1:
    :param t2:
    :return:
    '''
    candidate_graphquery_list = []
    current_nid = 1
    node_topic_entity = GroundedNode(nid=current_nid, node_type=t1, id=s1, type_class='', friendly_name="", question_node=0)
    current_nid += 1
    node_answer_entity = GroundedNode(nid=current_nid, node_type=t2, id=s2, type_class='', friendly_name="", question_node=1)
    p_answers = collections.defaultdict(set)
    for candidate in paths:
        cols = candidate.split("\t")
        if len(cols) != 2:
            continue
        answer_entity, relation = cols
        p_answers[relation].add(answer_entity)
    for p in p_answers:
        candidate_graphquery = dict()
        candidate_graphquery["querytype"] = '3_0_b'
        candidate_graphquery["nodes"] = [node_topic_entity, node_answer_entity]
        edge = GroundedEdge(start=node_answer_entity.nid, end=node_topic_entity.nid, relation=p)
        candidate_graphquery["edges"] = [edge]
        candidate_graphquery["path"] = p
        candidate_graphquery["denotation"] = list(p_answers[p])
        candidate_graphquery_list.append(candidate_graphquery)
    return candidate_graphquery_list

