import numpy as np
import time

# coupon rate of Par Bond
TWO_YEAR_RATE = 0.04
TRE_YEAR_RATE = 0.045
FOU_YEAR_RATE = 0.05
FIV_YEAR_RATE = 0.055
PAR_RATE = [0.035, 0.04, 0.045, 0.05, 0.055]

K = 100.0  # strike price of Par Bond

SIGMA = 0.1  # volatility
R0 = 0.035  # one-year forward interest rate


class BLOCK(object):
    """Block Diagram"""
    def __init__(self, value=0., coupon=0., rate=0.):
        self.block = '| V = {}\t|\n| C = {}\t|\n| R = {}%\t|'.format(value, coupon, rate*100)


class NODE(object):
    """Node for Binomial Tree"""
    def __init__(self, value=0., coupon=0., rate=0.):
        self.value = value
        self.coupon = coupon
        self.rate = rate


class BMATRIX(object):
    """Binomial Tree Matrix"""
    # use upper triangular matrix to store the structure
    def __init__(self, year=3):
        self.year = year
        self.root = np.array([NODE() for i in range((year+1)**2)]).reshape(year+1, year+1)
        
        
    # initial the matrix -> value & coupon before forward propagation
    def matrix_init(self, loc, c):
        for j in range(0, loc):
            for i in range(j+1):
                self.root[i][j].value = 0
                self.root[i][j].coupon = c
        for i in  range(loc):
            self.root[i][loc-1].value = K
    
    
    # calculate the node value
    # p & d & t using for pricing, p:price d:date t:type(1:callable 2:puttable)
    def forward_propagation(self, loc, p=100, d=float("inf"), t=1):
        loc_h = (loc[0], loc[1]+1)
        loc_l = (loc[0]+1, loc[1]+1)
        
        if not self.root[loc_h].value:
            self.forward_propagation(loc_h, p, d, t)
        V_h = self.root[loc_h].value
    
        if not self.root[loc_l].value:
            self.forward_propagation(loc_l, p, d, t)
        V_l = self.root[loc_l].value
        
        C  = self.root[loc_h].coupon
        R = self.root[loc].rate
        
        discount = 0.5 * ((V_h + C)/(1 + R) + (V_l + C)/(1 + R))
        
        # include an option
        if d <= loc[1]:
            self.root[loc].value = min(discount, p) if t == 1 else max(discount, p)
        # not include an option
        else:
            self.root[loc].value = discount
            
        return self.root[loc].value

    
    # build the binomial tree
    def build_binomial_interest_rate_tree(self, count):
        if count == 1:
            self.root[0, 0].rate = R0
            return 
        
        else:
            self.build_binomial_interest_rate_tree(count-1)
            self.root[0, 0].value = 0.
            C = PAR_RATE[count-1] * 100
            
            # use dichotomy to solve the root of rate
            lower, upper, result = 0., 1., 0.

            while(round(result, 3) != K):
                lower, upper = dichotomy(lower, upper, K, result)
                
                self.matrix_init(count+1, C)
                R_init = (lower + upper)/2
                
                # init the rate
                for i in reversed(range(count)):
                    self.root[i, count-1].rate = R_init
                    R_init = lognormal_rate(R_init) 
                
                result = self.forward_propagation((0, 0))
            return            
        

    # pricing for bond
    def pricing(self, t='Callable Bond', coupon_rate=0.0525, expiry=3, option_price=100, option_date=1):
        if t == 'Simple Bond':
            C = coupon_rate * 100
            self.matrix_init(expiry+1, C)
            result = self.forward_propagation((0, 0))
            tree.display()
            print 'The price of this Simple bond is ${}'.format(round(result, 4))
        elif t == 'Callable Bond':
            C = coupon_rate * 100
            self.matrix_init(expiry+1, C)
            result = self.forward_propagation((0, 0), option_price, option_date, 1)   
            tree.display()
            print 'The price of this Callable bond is ${}'.format(round(result, 4))
        elif t == 'Puttable Bond':
            C = coupon_rate * 100
            self.matrix_init(expiry+1, C)
            result = self.forward_propagation((0, 0), option_price, option_date, 2)   
            tree.display()
            print 'The price of this Puttable bond is ${}'.format(round(result, 4))
            
        
    def display(self):
        shape = (self.year * 2 - 1, self.year)
        
        # diagram is the matrix for diagram of all blocks
        diagram = [[' \t\t \n \t\t \n \t\t ' for i in range(shape[1])] for j in range(shape[0])]

        for j in range(self.year):
            for i in range(j+1):
                block = BLOCK(round(self.root[i][j].value, 3), round(self.root[i][j].coupon, 3), round(self.root[i][j].rate, 5))
                diagram[i * 2 + shape[1] - 1 - j][j] = block.block
        
        # change the format into the format which is able to print
        flatten = list()
        for line_before in diagram:
            line_before = '\n'.join(line_before).split('\n') + ['\n'] * 3
            line_after = list(np.array(line_before).reshape(shape[1]+1, 3).transpose().flatten())
            flatten += line_after
        
        # , controls the line feed
        print '\n', '- ' * 30
        for i in flatten:
            print i, 


    
# relationship between R_h & R_l
def lognormal_rate(r):
    return r * np.exp(2*SIGMA)


# dichotomy for figuring the rate
def dichotomy(lower, upper, target, result):
    # x & y changes in opposite direction
    return (lower, (lower + upper)/2) if result < target else  ((lower + upper)/2, upper)



if __name__ == '__main__':
    tree = BMATRIX(4)
    tree.build_binomial_interest_rate_tree(tree.year)
    tree.display()
    print 'Finish building binomial interest rate tree'
    
    tree.pricing('Simple Bond')
    tree.pricing('Callable Bond')
    tree.pricing('Puttable Bond')
    
    











