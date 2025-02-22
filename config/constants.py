r"""
constants
"""

# 所依赖的拓展库
REQUIRED_MODULES = {
    "bs4": "beautifulsoup4",
    "requests": "requests",
    "scipy": "scipy",
}

# 日志的路径
LOG_PATH = r"logs\log.md"

# 日志中的时间格式
STR_TIME_FORMAT = r"%Y-%m-%d %H:%M:%S"

# 输出结果的文件夹
RESULT_PATH = r"result"


# 登录选课系统的网站
XK_LOGIN_URL = "https://xk.fudan.edu.cn/xk/login.action"

# 选课系统网页 html 文档中，要提交的表单的 id 属性值
LOGIN_FORM_ID = "loginForm"

# 登录失败后，可能会返回包含以下四种错误信息的网页
LOGIN_FAIL_INFORMATION = {
	"用户名或密码错误": "incorrect username or password",
    "请输入验证码": "verification code required",
    "网络维护中": "server maintenance",
    "请不要过快点击": "click too quickly",
}

# 两次登录之间的时间间隔，用来避免“请不要过快点击”登录失败
LOGIN_INTERVAL_TIME = 0.13


# 选课系统的根目录
BASE_URL = "https://xk.fudan.edu.cn"

# 选课系统的主页
XK_HOME_URL = "https://xk.fudan.edu.cn/xk/home.action"

# 选课的入口页面
XK_STD_ELECT_COURSE_URL = "https://xk.fudan.edu.cn/xk/stdElectCourse.action"

# 选课的默认页面
XK_STD_ELECT_COURSE_DEFAULT_PAGE_URL = "https://xk.fudan.edu.cn/xk/stdElectCourse!defaultPage.action"

# 进入选课页面失败后，可能会返回包含以下两种错误信息的网页
ENTER_FAIL_INFORMATION = {
    "不在选课时间内": "outside selection period",
    "选课限制": "parameter error",
}

# 选课阶段
PHASES_INFORMATION = {
    "第一轮": "第一轮",
    "第二轮": "第二轮",
    "第三轮": "第三轮",
}

# 查询课程的 URL ，每轮选课都不一样的
XK_STD_ELECT_COURSE_QUERY_LESSON_URL = 'https://xk.fudan.edu.cn/xk/stdElectCourse!queryLesson.action?profileId=3045'

# 查询课程得到的预期错误
QUERY_ERROR_INFORMATION = {
    "请不要过快点击": "click too quickly",
    "error lessonNo length": "the lesson_no requires at least 6 characters",
    "error courseCode length": "the course_code requires at least 6 characters",
    "error courseName length": "the course_name requires at least 4 characters or 2 Chinese characters",
    "error no lessons": "At present, it is the peak stage of course selection. Please enter the precise lesson_no, course_code, and course_name to query.",
}

# 两次查询之间的时间间隔，用来避免“请不要过快点击”查询失败
QUERY_INTERVAL_TIME = 0.13

# 上午、下午、晚上分别有几节课
COURSES_COUNT = {
    "morning": 5,
    "afternoon": 5,
    "evening": 4,
}

# 每天最多有几节课
MAX_CLASSES_PER_DAY = sum(COURSES_COUNT.values())

# 选课限制：该类{key}课程不能超过最大选课{value}门数限制
COURSE_QUANTITY_LIMIT = {
    r"^PTSS110(?!058|059|060|061|092).*": 2,
    r"^(([0-9a-zA-Z]){3}|([0-9a-zA-Z]){4})1190.*|^FINE110.*": 1,
}

# 每节课的时间段，用于制作课程表
COURSE_TIME = [
    ["第一节", "8:00-8:45"],
    ["第二节", "8:55-9:40"],
    ["第三节", "9:55-10:40"],
    ["第四节", "10:50-11:35"],
    ["第五节", "11:45-12:30"],
    ["第六节", "13:30-14:15"],
    ["第七节", "14:25-15:10"],
    ["第八节", "15:25-16:10"],
    ["第九节", "16:20-17:05"],
    ["第十节", "17:15-18:00"],
    ["第十一节", "18:30-19:15"],
    ["第十二节", "19:25-20:10"],
    ["第十三节", "20:20-21:05"],
    ["第十四节", "21:15-22:00"],
]

# 课程表的表头，用于制作课程表
TABLE_HEADING = ["节次", "时间", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

# 通常开始安排考试的周次
EXAM_START_WEEK = 15

# 通常安排考试的最后周次
EXAM_END_WEEK = 18

# 数字与星期名称的双向映射
# Default: Monday is 0.
WEEKDAY_MAPPING = {
    0: "一",
    1: "二",
    2: "三",
    3: "四",
    4: "五",
    5: "六",
    6: "日",
    "一": 0,
    "二": 1,
    "三": 2,
    "四": 3,
    "五": 4,
    "六": 5,
    "日": 6,
}


# 校区代码
CAMPUS_CODES = {
    "H",
    "J",
    "F",
    "Z",
}

# 校区名
CAMPUS_NAMES = {
    "H": "邯郸校区",
    "J": "江湾校区",
    "F": "枫林校区",
    "Z": "张江校区",
}

# 在各校区间乘校车的通勤时间（单位：分钟，来源：高德地图）
CAMPUS_COMMUTE_TIMES = {
    ('H', 'J'): 17,
    ('J', 'H'): 14,
    ('H', 'F'): 34,
    ('F', 'H'): 39,
    ('H', 'Z'): 27,
    ('Z', 'H'): 32,
    ('J', 'F'): 40,
    ('F', 'J'): 41,
    ('J', 'Z'): 33,
    ('Z', 'J'): 39,
    ('F', 'Z'): 30,
    ('Z', 'F'): 32,
}


# 食堂代码

CANTEEN_CODES = {
    "H本部食堂",
    "H北区食堂",
    "H南区食堂",
    "H教工食堂",
    "J食堂",
    "Z食堂",
    "F食堂",
    "F清真",
}

# 教学楼楼的代码
TEACHING_BUILDING_CODES = {
    "H1",
    "H2",
    "H3",
    "H4",
    "H5",
    "H6",
    "HGX",
    "H逸夫楼",
    "H元·创中心",
    "H北区会馆",
    "H数值模拟实验室-光学楼B",
    "H杨咏曼楼",
    "H南区篮球场",
    "H南区健身房",
    "H院系自主", # 神奇的地名
    "JA",
    "Z2",
    "F1",
    "F2",
    "F枫林综合游泳馆地下篮球场",
}

# 寝室楼的代码
DORMITORY_BUILDING_CODES = {
    "H南区9",
}

# 楼的代码
BUILDING_CODES = CANTEEN_CODES | TEACHING_BUILDING_CODES | DORMITORY_BUILDING_CODES

# 楼名
BUILDING_NAMES = {
    "H1": "复旦大学邯郸校区第一教学楼",
    "H2": "复旦大学邯郸校区第二教学楼",
    "H3": "复旦大学邯郸校区第三教学楼",
    "H4": "复旦大学邯郸校区第四教学楼",
    "H5": "复旦大学邯郸校区第五教学楼",
    "H6": "复旦大学邯郸校区第六教学楼",
    "HGX": "复旦大学邯郸校区光华楼西辅楼",
    "H逸夫楼": "复旦大学邯郸校区逸夫楼",
    "H元·创中心": "复旦大学邯郸校区元·创中心",
    "H数值模拟实验室-光学楼B": "复旦大学邯郸校区兴业光学楼",
    "H杨咏曼楼": "复旦大学邯郸校区东区艺术教育中心",
    "H南区篮球场": "复旦大学邯郸校区南区篮球场",
    "H南区健身房": "复旦大学邯郸校区南区健身房",
    "H北区会馆": "复旦大学邯郸校区北区体育场",
    "H院系自主": "复旦大学邯郸校区院系自主",
    "H本部食堂": "复旦大学邯郸校区本部食堂旦苑餐厅",
    "H北区食堂": "复旦大学邯郸校区北区食堂",
    "H南区食堂": "复旦大学邯郸校区南区餐厅",
    "H教工食堂": "复旦大学邯郸校区教工食堂",
    "H南区9": "复旦大学邯郸校区南区学生公寓9号",
    "JA": "复旦大学江湾校区教学楼A号楼",
    "J食堂": "复旦大学江湾校区食堂",
    "Z2": "复旦大学张江校区2号教学楼",
    "Z食堂": "复旦大学张江校区学生餐厅",
    "F1": "复旦大学上海医学院第1教学楼",
    "F2": "复旦大学上海医学院第2教学楼",
    "F枫林综合游泳馆地下篮球场": "复旦大学上海医学院综合游泳馆",
    "F食堂": "复旦大学上海医学院西17号楼",
    "F清真": "复旦大学上海医学院枫林路校区西区清真餐厅",
}

# 楼的正门的经纬度
BUILDING_LOCATIONS = {
    "H1": (121.50182, 31.29732),
    "H2": (121.50452, 31.29778),
    "H3": (121.50442, 31.29808),
    "H4": (121.50165, 31.29847),
    "H5": (121.50473, 31.29543),
    "H6": (121.5044, 31.2949), # 这个精确度少一位
    "HGX": (121.50430, 31.29981),
    "H逸夫楼": (121.50166, 31.29919),
    "H元·创中心": (121.5048, 31.3006), # 这个精确度少一位
    "H数值模拟实验室-光学楼B": (121.50128, 31.29768),
    "H杨咏曼楼": (121.50852, 31.30105),
    "H南区篮球场": (121.50204, 31.29054),
    "H南区健身房": (121.50204, 31.29235),
    "H北区会馆": (121.49598, 31.30078),
    "H院系自主": (121.50365, 31.29755), # 定位到毛像
    "H本部食堂": (121.50631, 31.30085),
    "H北区食堂": (121.49720, 31.30110),
    "H南区食堂": (121.50027, 31.29203),
    "H教工食堂": (121.50490, 31.29480),
    "H南区9": (121.50037, 31.29136),
    "JA": (121.5054, 31.33632),
    "J食堂": (121.50385, 31.33589),
    "Z2": (121.5984, 31.1912),
    "Z食堂": (121.59685, 31.18928),
    "F1": (121.4488, 31.19535),
    "F2": (121.4485, 31.1955),
    "F枫林综合游泳馆地下篮球场": (121.4510, 31.19575),
    "F食堂": (121.4493, 31.1951),
    "F清真": (121.45012, 31.19726),
}

# 寝室代码
DORMITORY_CODE = "H南区9301"
