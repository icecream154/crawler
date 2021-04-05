def content_filter(ori_content: str, replace_list: [(str, str)]):
    for rep in replace_list:
        ori_content = ori_content.replace(rep[0], rep[1])

    return ori_content
