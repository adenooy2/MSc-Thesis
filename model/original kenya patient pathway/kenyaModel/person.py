import numpy as np


class person():

    def __init__(self, hiv_status):
        self.hiv_status = hiv_status
        self.tb_test = "no_test"
        self.tb_test_result = "no_test_res"
        self.tb_notification = "no_notification"
        self.num_diagnosticTest = 0
        self.numVisits = 0
        self.sample_status = "no_sample"
        self.tb_test_type = "no_test"
        self.tb_test_reach="no_test"
        self.smear_status = "none"
        self.screen_status = "unknown"
        self.tb_empiric="no"

    def assign_tb_status(self, prev_tb_hiv, prev_tb_hiv_neg, prev_etb_hiv, prev_etb_hiv_neg):
        randnum = np.random.rand()

        if self.hiv_status == "hiv_pos":

            if randnum < prev_tb_hiv:
                self.tb_status = "tb_pulmonary"
            elif prev_tb_hiv <= randnum < prev_tb_hiv + prev_etb_hiv:
                self.tb_status = "tb_extrapulmonary"
            else:
                self.tb_status = "tb_negative"
        else:

            if randnum < prev_tb_hiv_neg:
                self.tb_status = "tb_pulmonary"
            elif prev_tb_hiv_neg <= randnum < prev_tb_hiv_neg + prev_etb_hiv_neg:
                self.tb_status = "tb_extrapulmonary"
            else:
                self.tb_status = "tb_negative"

    def tb_cascade_base(self, p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access, p_xpert, p_onsite,
                   p_reach_1, sens_xpert, spec_xpert, sens_smear, spec_smear, p_return,p_empiric):
        self.tb_visit_and_provide_sample(p_test_offered, p_visit, p_visit_2, p_test_access)
        self.sample_collection(p_no_sample, p_visit)
        self.site_testing(p_xpert, p_onsite, p_reach_1)

        if self.tb_test_reach == "test":
            if self.tb_test_type == "xpert":
                sens = sens_xpert
                spec = spec_xpert
            else:
                sens = sens_smear
                spec = spec_smear

            if self.tb_status == "tb_negative":
                self.tb_negative_diagnostic(spec, p_return)
            else:
                self.tb_positive_diagnostic(sens, p_return)

        if self.tb_notification == "tb_negative":
            if self.tb_test_type=="smear":
                if np.random.rand()<p_empiric:
                    self.tb_notification="tb_positive"
                    self.tb_empiric="yes"

    def tb_cascade_scen(self, p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access, p_xpert, p_onsite,
                   p_reach_1, sens,spec, p_return,p_empiric):

        self.tb_visit_and_provide_sample(p_test_offered, p_visit, p_visit_2, p_test_access)
        self.sample_collection(p_no_sample, p_visit)
        self.site_testing(p_xpert, p_onsite, p_reach_1)

        if self.tb_test_reach == "test":

            if self.tb_status == "tb_negative":
                self.tb_negative_diagnostic(spec, p_return)
            else:
                self.tb_positive_diagnostic(sens, p_return)



    def tb_visit_and_provide_sample(self, p_test_offered, p_visit, p_visit_2, p_test_access):
        # print("in test sample cascade")

        # print("ptest ",p_test_1)
        """ # Does patient seek care and provide samples (may require 2/3 visits)"""
        if np.random.rand() < p_visit:
            # patient sought care for symptoms
            self.numVisits = self.numVisits + 1
            # patient offered a test / refered for diagnostics
            if np.random.rand() < p_test_offered:

                # site accessed has TB diagnostics or referral syste,
                if np.random.rand() < p_test_access:
                    self.tb_test = "test"
                    self.sample_status = "first_sample"
                    self.num_diagnosticTest = self.num_diagnosticTest + 1

                else:
                    # refferred to another site
                    if np.random.rand() < p_visit_2:
                        # patient attends referred diagnostic
                        self.numVisits = self.numVisits + 1
                        self.tb_test = "test"
                        self.sample_status = "first_sample"
                        self.num_diagnosticTest = self.num_diagnosticTest + 1

    def sample_collection(self, p_no_sample, p_visit):
        if self.tb_test == "test":
            if np.random.rand() < p_no_sample:
                # unable to initially provide a sample - must return
                if np.random.rand() < p_visit:
                    self.tb_test = "test"
                    self.numVisits = self.numVisits + 1
                    self.sample_status = "second_sample"
                else:
                    self.tb_test = "no_test"
                    self.num_diagnosticTest = self.num_diagnosticTest - 1
                    self.sample_status = "no_sample"

    def site_testing(self, p_xpert, p_onsite, p_reach_1):

        if self.tb_test == "test":
            # onsite testing
            if np.random.rand() < p_onsite:
                self.tb_test_reach = "test"
                if np.random.rand() < p_xpert:
                    self.tb_test_type = "xpert"
                else:
                    self.tb_test_type = "smear"

            else:
                # offsite testing
                if np.random.rand() < p_reach_1:
                    # sample reaches lab and is tested
                    self.tb_test_type = "xpert"
                    self.tb_test_reach = "test"

    def tb_negative_diagnostic(self, spec, p_return):
        # For people without TB who have provided samples
        if np.random.rand() < spec:
            # true neg
            self.tb_test_result = "tb_negative"

            if np.random.rand() < p_return:
                self.tb_notification = "tb_negative"
                self.numVisits = self.numVisits + 1

        else:
            # false pos
            self.tb_test_result = "tb_positive"
            if np.random.rand() < p_return:
                self.numVisits = self.numVisits + 1
                self.tb_notification = "tb_positive"

    def tb_positive_diagnostic(self, sens, p_return):
        # For people with TB who have provided samples
        if np.random.rand() < 1 - sens:
            # true neg
            self.tb_test_result = "tb_negative"

            if np.random.rand() < p_return:
                self.tb_notification = "tb_negative"
                self.numVisits = self.numVisits + 1
        else:
            # false pos
            self.tb_test_result = "tb_positive"

            if np.random.rand() < p_return:
                self.numVisits = self.numVisits + 1
                self.tb_notification = "tb_positive"

    def tb_screen(self,p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access, p_xpert, p_onsite,
                            p_reach_1, sens_xpert, spec_xpert, sens_smear, spec_smear, p_return,p_empiric,sens_sc,spec_sc):
        if self.tb_status == "tb_negative":
            if np.random.rand() < spec_sc:
                self.screen_status = "tb_negative"
            else:
                self.screen_status = "tb_positive"
        else:
            if np.random.rand() < sens_sc:
                self.screen_status = "tb_positive"
            else:
                self.screen_status = "tb_negative"

        if self.screen_status == "tb_positive":
            self.tb_cascade_base( p_visit, p_visit_2, p_test_offered, p_no_sample, p_test_access, p_xpert, p_onsite,
                   p_reach_1, sens_xpert, spec_xpert, sens_smear, spec_smear, p_return,p_empiric)
