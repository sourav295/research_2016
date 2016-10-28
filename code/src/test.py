import itertools
import numpy

'''COST BENEFIT'''
cost_benefit_SDN_list = list(numpy.arange(1, 5.5, 1))
cost_benefit_NFV_list = []

'''DELAY DETRIMENT'''
delay_detriment_SDN_list = list(numpy.arange(1, 5.5, 1))
delay_detriment_NFV_list = []


dummy_value = 10    #just to ensure itertools.product does not become [] for one empty value
for conf_list in cost_benefit_SDN_list, cost_benefit_NFV_list, delay_detriment_SDN_list, delay_detriment_NFV_list:
    if not conf_list:
        conf_list.append(dummy_value)

sdn_nfv_config_combinations = list(itertools.product(   cost_benefit_SDN_list       ,\
                                                        cost_benefit_NFV_list       ,\
                                                        delay_detriment_SDN_list    ,\
                                                        delay_detriment_NFV_list     \
                                                    ))
                                        
print len(sdn_nfv_config_combinations)
for cost_benefit_SDN, cost_benefit_NFV, delay_detriment_SDN, delay_detriment_NFV in sdn_nfv_config_combinations:
    x=cost_benefit_SDN

