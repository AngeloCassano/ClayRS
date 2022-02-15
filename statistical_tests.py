from scipy.stats import ttest_ind, ranksums
import numpy as np
import pandas as pd


class pairedtTest:
    @staticmethod
    def t_test(sample_list1, sample_list2):
        """
                T-student

                Calculates the T-test for the means of TWO INDEPENDENT samples of scores.

                This is a two-sided test for the null hypothesis that 2 independent samples have identical
                average (expected) values

                This test assumes that the populations have identical variances.
                """
        t, p = ttest_ind(sample_list1, sample_list2)
        print("=== T- Student Analysis ===")
        print("The calculated t-statistic: " + str(t))
        print("The two-tailed p-value: " + str(p) + "\n")



class wilcoxonTest:
    @staticmethod
    def wilcoxon(sample_list1, sample_list2):
        """
                Wilcoxon

                The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from
                the same distribution. In particular, it tests whether the distribution of the differences x - y
                is symmetric about zero. It is a non-parametric version of the paired T-test.
                """

        t, p = ranksums(sample_list1, sample_list2)
        print("=== Wilcoxon Analysis ===")
        print("The calculated t-statistic: " + str(t))
        print("The two-tailed p-value: " + str(p) + "\n")


