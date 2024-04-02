
def tonic_get_root_of_node(obj):
    if obj.startswith('|'):
        split_obj = obj.split('|')
        if split_obj:
            return split_obj[1]
    return None
def tonic_get_all_roots_of_list(list_of_nodes):
    import maya.cmds as cmds
    all_roots = []

    for n in list_of_nodes:
        if cmds.nodeType(n) == 'transform':
            r = tonic_get_root_of_node(n)
            if r:
                all_roots.append(r)
    return list(set(all_roots))

def tonic_get_all_namespaces_of_list(list_of_nodes):
    import maya.cmds as cmds
    all_ns = []
    for n in list_of_nodes:
        r = tonic_get_root_of_node(n)
        if r and ':' in r:
            split_obj = r.split(':')
            ns = split_obj[0]
            all_ns.append(ns)
    return list(set(all_ns))


