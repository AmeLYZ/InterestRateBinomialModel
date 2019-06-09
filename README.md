# Interest Rate Binomial Model
程序实现利率二叉树定价算法

> 参考链接
- [期权定价原理](https://www.jianshu.com/p/1edd7c0868af)

## 背景介绍
我们知道在对债券定价的时候，运用同一个利率去贴现债券的现金流是不合适的。因此引入了收益率曲线，只要未来的现金流确定，就可以根据收益率曲线计算任何债券的价格。
![公式1]('image/formula1.png')
但是分析嵌入期权的债券时,由于未来的现金流会变动,因此无法使用上述方法进行定价。  
我们引入了 Interest rate model，假设利率水平变化符合布朗运动（随机对数正态模型），且利率波动率保持不变。通过当前的利率水平和利率波动率就能画出利率变化的二叉树。
## 步骤
### 构建利率二叉树  
这里需要预设一系列平价债券的票息率用于计算利率。
```Python
# coupon rate of Par Bond
R0 = 0.035  # one-year forward interest rate
TWO_YEAR_RATE = 0.04
TRE_YEAR_RATE = 0.045
FOU_YEAR_RATE = 0.05
FIV_YEAR_RATE = 0.055
PAR_RATE = [0.035, 0.04, 0.045, 0.05, 0.055]
K = 100.0  # strike price of Par Bond

SIGMA = 0.1  # volatility
```
利用两年期的平价债券计算第一年的一年期远期利率。利用三年期的平价债券计算第二年的一年期远期利率。  
由于某个节点上的价值取决于将来的现金流，而将来的现金流又取决于  
- 从现在起一年的债券价值
- 从现在起一年后的息票利息支付  

在考虑利率波动性的情况下，需要首先确定一年后较高的一年期远期利率和一年后较低的远期利率。根据布朗运动的假设，有如下等量关系：
![公式2]('image/formula2.png')
先将这两个数值假设出来（用作第二年的现金流贴现利率）。已知两年期的平价债券在第二年的时候债券价值为债券的执行价格加上当年的票息。通过远期利率贴现得到V_h和V_l。再将V_h和V_l贴现到第一年（已知当年的一年期远期利率），如果贴现结果等于债券价格（由于是平价发行，即为票面价值），说明假设的一年后较高的一年期远期利率和一年后较低的远期利率是合理的，否则重新假设直到合理为止。  
![公式3]('image/formula3.png')
由于利率与V_0的变化是反比例变化的（利率越高，V_0越低），因此可以运用二分法逐步逼近正解。
计算出第一年的较高的一年期远期利率和一年后较低的远期利率后，用同样的方法利用三年期的平价债券计算第二年的一年期远期利率。  

### 为债券定价
直接将票面利息带入构建好的利率二叉树即可，这一步也就是将未来现金流的树与利率树相结合，贴现的利率就是利率二叉树的利率。
- 不含权的债券->每个节点无额外判断
- 可赎回债券->每个节点判断min(discount, P)
- 可回售债券->每个节点判断max(discount, P)

## 程序说明
### 类
构建了BMATRIX类，使用上三角矩阵储存二叉树。二叉树的节点使用NODE类储存。BLOCK类用于二叉树可视化，每一个BLOCK实例是一个节点。
![BLOCK类]('image/image.png')
```Python
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
```
### 类方法
```Python
# 创建4年/4步二叉树
tree = BMATRIX(4)
# 求解利率二叉树
tree.build_binomial_interest_rate_tree(tree.year)
# 将前两步的节点value对象置零，并将coupon对象赋值为3；将第3步的节点value对象置为100（平价债券价格）
tree.matrix_init(loc=2, c=3)
# 求解loc节点的value
tree.forward_propagation(loc=(0, 0))
# 为一个票息率5.25%，3年期，可以在1年后以100赎回的可赎回债券定价
tree.pricing(t='Callable Bond', coupon_rate=0.0525, expiry=3, option_price=100, option_date=1)
# 二叉树可视化
tree.display()
```
### 函数
```Python
# 在lower和upper之间使用二分法求解，需要搭配while使用
dichotomy(lower, upper, target, result)
```
