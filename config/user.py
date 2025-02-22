r"""
User's data.
"""

from csv import reader

# 学号和密码
USERNAME = "你的学号"
PASSWORD = "你的 UIS 密码"

# 你已经选了的课的数量
SELECTED_COURSES_COUNT = 9

# 为你排出的课表数量上限，取得分最高的`MAX_SCHEDULES_TO_OUTPUT`份课表输出
# 如果可行方案少于`MAX_SCHEDULES_TO_OUTPUT`种，将只输出可行的那几种
MAX_SCHEDULES_TO_OUTPUT = 10

# 可以排已经选满的课吗？
# 此选项在第二轮或第三轮选课时有用
# 若`FULL_OK`为`False`，那么在第二轮或第三轮选课时，会过滤掉那些已经报满了的课
FULL_OK = False


# “通勤时间”和“课程评分”在课程表得分中所占的权重
COMMUTE_TIME_WEIGHT = 0.0
COURSE_SCORE_WEIGHT = 1.0


# 最佳选课人数比例（已选/上限）
OPTIMAL_PROPORTION_OF_SELECTION = 1.618 # 如果一门课程的 已选人数/上限人数 等于这个值，那么它的“得分”将为`1`（满分）。得分将按照正态概率曲线映射得到

# 正态分布密度函数的标准差
SIGMA = 0.618 # 这个值必需大于`0`

# 检查`EMPTY_COURSE_SCORE`是否符合要求
assert SIGMA > 0, f"`SIGMA` 必需大于`0`，但是你输入了{SIGMA}"


# 读取 course_codes.csv
with open(r"config/course_codes.csv", "r", encoding="gbk") as file:
    COURSE_CODES = {row[0]: row[1] for row in reader(file)}

# 读取 tags.csv
with open(r"config/tags.csv", "r", encoding="gbk") as file:
    TAGS_COUNT = {row[0]: int(row[1]) for row in reader(file)}
