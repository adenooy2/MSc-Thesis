import numpy as np
from person import person
from cohort import cohort
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 5)
# cohort characteristics
#N_size = [2700, 7300, 10000]
N_size=10000
prevs = [10,30]
propHIV=0.086
runs = 10
for prev in prevs:

    if prev == 10:
        modelProbs = pd.read_excel(
            '/Users/adenooy/Documents/AMC/TB Cascade Modelling/modelProbs/Kenya_final_probs.xlsx',
            sheet_name="baseline_10")
    else:
        modelProbs = pd.read_excel(
            '/Users/adenooy/Documents/AMC/TB Cascade Modelling/modelProbs/Kenya_final_probs.xlsx',
            sheet_name="baseline_30")

    prev_tb_hiv = modelProbs.loc[modelProbs["variable"] == "prev", ["value_hiv_pos"]].values.astype(float)
    prev_tb_hiv_neg = modelProbs.loc[modelProbs["variable"] == "prev", ["value_hiv_neg"]].values.astype(float)
    prev_etb_hiv = modelProbs.loc[modelProbs["variable"] == "prev", ["value_hiv_pos_eptb"]].values.astype(float)
    prev_etb_hiv_neg = modelProbs.loc[modelProbs["variable"] == "prev", ["value_hiv_neg_eptb"]].values.astype(float)

    hiv_prob_list = np.random.random_sample(size=N_size)
    hiv_stat_list = ["hiv_pos" if x < propHIV else "hiv_neg" for x in hiv_prob_list]


    simCond=["baseline"]
    #simCond=["scenXpert"]
    #simCond = ["baseline","scen","scenXpert"]
    #simCond = ["calibration", "scen", "baseline"]

    for sc in simCond:
        if sc == "baseline" or sc =="scenXpert":
            if sc=="baseline":
                scenarios = ["scenBase"]
            else:
                #scenarios = ["scenXpert"]
                scenarios = ["scen_1", "scen_2", "scen_3", "scen_4", "scen_5", "scen_6"]

            sensitivity = ["base"]
            specificity = ["base"]
        elif sc=="scen":
            base_cascades = ["scen"]
            #sensitivity = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
            #specificity = [0.998, 0.9944, 0.9908, 0.9872, 0.9836, 0.98]
            sensitivity = [0.4,0.5,0.6]
            specificity = [0.998,0.998,0.998]

            scenarios = ["scen_1", "scen_2", "scen_3", "scen_4","scen_5","scen_6"]

        for scen in scenarios:
            N = N_size

            for k in range(0, len(sensitivity)):

                sens=sensitivity[k]
                spec=specificity[k]

                for it in range(0, runs):
                    pop = cohort()
                    for per_num in range(0, N):
                        p = person(hiv_stat_list[per_num])
                        p.assign_tb_status(prev_tb_hiv, prev_tb_hiv_neg, prev_etb_hiv, prev_etb_hiv_neg)

                        if p.hiv_status == "hiv_neg":
                            if p.tb_status == "tb_negative" or p.tb_status == "tb_pulmonary":
                                comb = "value_hiv_neg"
                            else:
                                comb = "value_hiv_neg_eptb"
                        else:
                            if p.tb_status == "tb_negative" or p.tb_status == "tb_pulmonary":
                                comb = "value_hiv_pos"
                            else:
                                comb = "value_hiv_pos_eptb"

                        # Standard params:
                        p_visit = modelProbs.loc[modelProbs["variable"] == "p_visit", [comb]].values.astype(float)
                        p_visit_2 = modelProbs.loc[modelProbs["variable"] == "p_visit_2", [comb]].values.astype(float)
                        p_test_access = modelProbs.loc[modelProbs["variable"] == "p_test_access", [comb]].values.astype(
                            float)
                        p_empiric = modelProbs.loc[
                            modelProbs["variable"] == "p_empiric", [comb]].values.astype(float)

                        p_test_offered = modelProbs.loc[modelProbs["variable"] == "p_test_offered", [comb]].values.astype(float)
                        p_no_sample = modelProbs.loc[modelProbs["variable"] == "p_no_sample", [comb]].values.astype(
                            float)
                        #p_onsite = modelProbs.loc[modelProbs["variable"] == "p_onsite", [comb]].values.astype(
                         #   float)
                        p_onsite=1
                        p_reach_1 = modelProbs.loc[modelProbs["variable"] == "p_reach_1", [comb]].values.astype(
                            float)
                        p_return = modelProbs.loc[modelProbs["variable"] == "p_return", [comb]].values.astype(float)
                       # p_xpert = modelProbs.loc[modelProbs["variable"] == "p_xpert", [comb]].values.astype(float)
                        p_xpert=1
                        spec_xpert = modelProbs.loc[modelProbs["variable"] == "spec_xpert", [comb]].values.astype(
                            float)
                        sens_xpert = modelProbs.loc[modelProbs["variable"] == "sens_xpert", [comb]].values.astype(
                            float)
                        spec_smear = modelProbs.loc[modelProbs["variable"] == "spec_smear", [comb]].values.astype(
                            float)
                        sens_smear = modelProbs.loc[modelProbs["variable"] == "sens_smear", [comb]].values.astype(
                            float)

                        # on site sample collection or same clinical enocunter
                        if scen in ["scen_2", "scen_3", "scen_5", "scen_6"]:
                            p_onsite = 1
                            p_xpert=1

                        # same clinical enocunter
                        if scen in ["scen_3", "scen_6"]:
                            p_return = 1
                            p_test_access=1
                            p_visit_2=1

                        # non sputum
                        if scen in ["scen_4", "scen_5", "scen_6"]:
                            if p.tb_status == "tb_negative" or p.tb_status == "tb_pulmonary":
                                p_no_sample = 0

                            p_test_offered = 1

                        if sc =="baseline":
                            p.tb_cascade_base( p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access, p_xpert, p_onsite,
                                p_reach_1, sens_xpert, spec_xpert, sens_smear, spec_smear, p_return,p_empiric)
                        elif sc=="scenXpert":
                            p.tb_cascade_scen(p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access,
                                              p_xpert, p_onsite,
                                              p_reach_1, sens_xpert, spec_xpert, p_return, p_empiric)

                        else:
                            p.tb_cascade_scen( p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access,
                                            p_xpert, p_onsite,
                                            p_reach_1, sens, spec, p_return, p_empiric)

                        pop.add_person(p)
                    # Results Table
                    att = []

                    for attribute, value in p.__dict__.items():
                        att.append(attribute)

                    #print(att)
                    resTable = pd.DataFrame(index=range(N), columns=att)

                    for j in range(0, N):
                        val = []
                        for attribute, value in pop.get_person(j).__dict__.items():
                            val.append(value)
                        #print(val)
                        resTable.iloc[j] = val
                    #print(resTable)
                    #path = [
                     #   "//Users/adenooy/Documents/AMC/TB Cascade Modelling/kenya/results/diagnostic/second/",
                      #  scen,
                       # "_prev_", str(prev), "_sens_", str(sens), "_spec_", str(spec), "_run_",
                        #str(it), ".xlsx"]

                    path = [
                        "/Users/adenooy/Documents/AMC/TB Cascade Modelling/smearAnalysis/xpert/kenya/",
                        scen,
                         "_prev_", str(prev), "_sens_", "xpert", "_spec_", str(spec), "_run_",
                         str(it), ".xlsx"]

                    resTable.to_excel(''.join(n for n in path))
