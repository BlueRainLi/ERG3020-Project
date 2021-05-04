
def fol_nl_gene(input_fol):
    uni_dict = {'pro': [], 'hyp': []}
    if "<=>" in input_fol:
        split_result = input_fol.split("<=>")
        print("<=>", split_result)
    elif "=>" in input_fol:
        split_result = input_fol.split("=>")
        print("=>", split_result)
    else:
        print("Predicates seems invalid!")
        return
    uni_dict['pro'] = split_result[0]
    uni_dict['hyp'] = split_result[1]

    for i in uni_dict.keys():
        if 'v' in uni_dict[i]:
            split_result_2 = uni_dict[i].split('v')
        elif '^' in uni_dict[i]:
            split_result_2 = uni_dict[i].split('^')
        else:
            pass


fol_nl_gene("aaaa=>b")

