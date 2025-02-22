r"""
class: Course
"""

from re import fullmatch
from functools import cache
from itertools import product

from scipy.stats import norm

from config.user import OPTIMAL_PROPORTION_OF_SELECTION, SIGMA
from src.model.exam_time import ExamTime
from src.model.arrangement import Arrangement


class Course():
    r"""
    课程类。

    ## 属性

    - `arrangements: list[Arrange]`：安排信息，pass
    - `campusCode: str`：上课所在的校区代码，如`"H"`。
    - `campusName: str`：上课所在的校区名，如`"邯郸校区"`。
    - `canApplyPnp: bool`：能否申请 PNP，如`False`。
    - `credits: float`：学分，如`5.0`。
    - `courseCode: str`：课程代码，如`"MATH120017"`。
    - `courseId: str`：标识（比较小的那个），如"42996"。
    - `courseName: str`：课程名，如`"数学分析BII"`。
    - `courseNo: str`：课程序号，如`"MATH120017.06"`。
    - `courseTypeCode: str`：课程类型代码，如`"02_03_01"`。
    - `courseTypeId: int`：课程类型标识，如`113`。
    - `courseTypeName: str`：课程类型名，如`"经管类I组"`。
    - `endWeek: int`：结束时的周数，如`16`。
    - `examFormName: str`：期末考试方式，如`"闭卷"`。
    - `examTime: ExamTime`：期末考试时间，如`ExamTime(datetime.datetime(2025, 6, 13, 15, 30), datetime.datetime(2025, 6, 13, 17, 30), 17, 4)`。
    - `examTimeString: str`：期末考试时间（字符串形式），等价于`str(self.examTime)`，如`"2025-06-13 15:30-17:30 第17周 星期五"`。
    - `hasTextBook: bool`：是否有教材，例如`false`。
    - `id: str`：课程标识（比较大的那个），如`"737991"`。
    - `isAPlus: bool`：是否含 A+ 成绩，如`True`。
    - `limitCount: int`：选课人数上限，如`100`。
    - `period: int`：总时间（单位：课时），如`108`。
    - `remark: str`：备注，如`"递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。"`。
    - `scheduled: bool`：是否被安排，如`true`。
    - `score: float`：对这门课的评分。
    - `selectCount: int`：当前已选人数，如`51`。
    - `startWeek: int`：开始时的周数，如`1`。
    - `teachDepartName: str`：开课院系名，如`"航空航天系"`。
    - `teacherNames: list[str]`：授课老师们的姓名，可能有多个，如：`["谢锡麟"]`、`["郑治龙", "邱国"]`。
    - `teachers: str`：以`','`分隔的老师们的姓名，如`"谢锡麟"`、`"郑治龙,邱国"`。
    - `textbooks: str`：教材名，如`""`。
    - `weekHour: float`：周课时，如`6.0`。
    - `withdrawable: bool`：是否可申请退课，如`True`。


    鉴于这两个事实：
    - 选的人数越多，这门课的质量就越高。
    - 选的人数越多，这门课就越难选到。
    
    给这门课评分。选的人太少或太多都会降低这门课的得分，当 选课人数/上限人数 = OPTIMAL_PROPORTION_OF_SELECTION 时，得满分（`1`分）。
    """

    # 可以从`lessonJSON`原封不动赋过来的键值对的键
    unchangedJSONKeys = {
        "campusCode",
        "campusName",
        "canApplyPnp",
        "credits",
        "courseTypeCode",
        "courseTypeId",
        "courseTypeName",
        "endWeek",
        "examFormName",
        "hasTextBook",
        "isAPlus",
        "period",
        "remark",
        "scheduled",
        "startWeek",
        "teachDepartName",
        "teachers",
        "textbooks",
        "weekHour",
        "withdrawable",
    }

    # `__init__`方法需要传入的参数名，就比`unchangedJSONKeys`多了一些
    initializationParameterNames = unchangedJSONKeys | {
        "arrangements",
        "courseCode",
        "courseId",
        "courseName",
        "courseNo",
        "examTimeString",
        "id",
    }

    # 以课程`id`为键，以`{"sc": 已选人数, "lc": 上限人数}`为值的字典
    lessonId2Counts = {}

    # 储存已经创建过了的课程实例
    courses = {}


    def __init__(self, **attributes):
        r"""
        将提供的参数作为属性来初始化。

        ## 参数

        - `arrangeInfo: list[Arrange]`
        - `campusCode: str`
        - `campusName: str`
        - `canApplyPnp: bool`
        - `credits: float`
        - `courseCode: str`
        - `courseId: str`
        - `courseName: str`
        - `courseNo: str`
        - `courseTypeCode: str`
        - `courseTypeId: int`
        - `courseTypeName: str`
        - `endWeek: int`
        - `examFormName: str`
        - `examTimeString: str`
        - `hasTextBook: bool`
        - `id: str`
        - `isAPlus: bool`
        - `period: int`
        - `remark: str`
        - `scheduled: bool`
        - `startWeek: int`
        - `teachDepartName: str`
        - `teachers: str`
        - `textbooks: str`
        - `weekHour: float`
        - `withdrawable: bool`
        """

        for (name, value) in attributes.items():
            setattr(self, name, value)

        self.examTime = ExamTime.fromString(self["examTimeString"])
        self.teacherNames = self["teachers"].split(",")
        self.selectCount, self.limitCount = self.getCount(self["id"])

        # 评分
        self.score = self.norm(self.selectCount / self.limitCount)

        # 与自己的安排建立联系
        for arrangement in self["arrangements"]:
            arrangement.course = self


    def __getitem__(self, name: str) -> object:
        r"""
        索引取值。返回`self`的名为`name`的成员。

        ## 返回

        - 要取的值。

        ## 异常
        
        1. `TypeError`：如果`name`的类型不是字符串。
        2. `AttributeError`：如果`self`没有名为`name`的成员。
        """

        return getattr(self, name)


    def __setitem__(self, name: str, value: object):
        r"""
        索引设值。将`self`的`name`属性设为`value`。

        ## 返回

        - `None`。

        ## 异常

        - `TypeError`：如果`name`的类型不是字符串。
        """

        setattr(self, name, value)


    def __hash__(self) -> int:
        return hash(self["id"])


    def __repr__(self) -> str:
        r"""
        返回对象的正式字符串表示，可用于重新创建该对象。

        ## 返回

        - `str`: 包含类名及初始化所需参数名称和值的字符串。

        ## 示例

        ```python
        "Course(weekHour=6.0, courseNo='MATH120017.06', id='737991', isAPlus=True, teachDepartName='航空航天系', courseCode='MATH120017', hasTextBook=False, period=108, startWeek=1, examTimeString='2025-06-13 15:30-17:30 第17周 星期五', courseTypeId=113, arrangements=(Arrangement(weekStateDigest='1-16', startUnit=11, roomsString='在线教学', endUnit=13, weekState='01111111111111111000000000000000000000000000000000000'), Arrangement(weekStateDigest='1-16', startUnit=6, roomsString='HGX507', endUnit=10, weekState='01111111111111111000000000000000000000000000000000000')), campusName='邯郸校区', courseName='数学分析BII', courseTypeCode='02_03_01', endWeek=16, scheduled=True, examFormName='闭卷', remark='递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。', withdrawable=True, campusCode='H', credits=5.0, textbooks='', courseId='42996', teachers='谢锡麟', canApplyPnp=False, courseTypeName='经管类I组')"
        ```
        """

        # 初始化对象所需要的参数名和值
        parameters = ", ".join(f"{para_name}={repr(self[para_name])}" for para_name in self.initializationParameterNames)

        return f"{type(self).__name__}({parameters})"


    def __str__(self) -> str:
        r"""
        以`"[课程序号]课程名"`的形式输出。
        """

        return f"[{self['courseNo']}]{self['courseName']}"


    def getDtailString(self) -> str:
        r"""
        以字符串"课程序号\t课程代码\t课程名称\t开课院系\t学分\t教师\t周课时\t校区\t备注\t已选/上限\t课程安排\t考试安排\t是否含A+成绩\t是否可申请P/NP"的形式输出。

        ## 示例

        ```python
        "MATH120017.06\tMATH120017\t数学分析BII\t航空航天系\t5.0\t谢锡麟\t6.0\t邯郸校区\t递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。\t51/100\t1-16周\n星期日 11-13节 在线教学\n1-16周\n星期五 6-10节 HGX507\t2025-06-13 15:30-17:30 第17周 星期五 [闭卷]\t是\t否"
        ```
        """

        return "\t".join((
            self["courseNo"],
            self["courseCode"],
            self["courseName"],
            self["teachDepartName"],
            str(self["credits"]),
            self["teachers"],
            str(self["weekHour"]),
            self["campusName"],
            self["remark"],
            f"{self["selectCount"]}/{self["limitCount"]}",
            "\n".join(map(str, self["arrangements"])),
            f"{self["examTimeString"]} [{self["examFormName"]}]",
            {True:"是", False:"否"}[self["isAPlus"]],
            {True:"是", False:"否"}[self["canApplyPnp"]],
        ))


    @classmethod
    def getCount(cls, id: str) -> tuple[int]:
        r"""
        以`(已选人数, 限制人数)`的形式返回`id`属性为`id`的课程的已选人数和限制人数。
        """

        return (cls.lessonId2Counts[id]["sc"], cls.lessonId2Counts[id]["lc"])


    @classmethod
    def fromJSON(cls, lessonJSON: dict[str, object]) -> "Course":
        r"""
        根据给定的 JSON 数据（字典格式）创建并返回一个新的 `Course` 实例。

        ## 参数

        - `lessonJSON`（`dict[str, object]`）：包含课程信息的字典。

        ## 返回

        - `Course`: 根据提供的数据创建的新 `Course` 实例。

        ## 异常

        - `KeyError`: 如果输入字典缺少必要的键。
        - `TypeError`: 如果尝试将不正确的类型用于特定字段。

        ## 注意

        - 执行此方法耗时约 0.0006 秒。

        ## 示例

        ```python
        import json

        Course.lessonId2Counts = {
            '737991':{
                "sc":51,
                "lc":100
            },
            '739850':{
                "sc":101,
                "lc":145
            },
            '739778':{
                "sc":5,
                "lc":15
            }
        }

        lessonJSONString = '''
        {
            "no":"MATH120017.06",
            "courseTypeName":"经管类I组",
            "code":"MATH120017",
            "campusName":"邯郸校区",
            "scheduled":true,
            "hasTextBook":false,
            "remark":"递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。",
            "teachDepartName":"航空航天系",
            "textbooks":"",
            "canApplyPnp":false,
            "credits":5.0,
            "withdrawable":true,
            "teachers":"谢锡麟",
            "weekHour":6.0,
            "id":737991,
            "endWeek":16,
            "courseId":42996,
            "courseTypeCode":"02_03_01",
            "startWeek":1,
            "period":108,
            "campusCode":"H",
            "courseTypeId":113,
            "arrangeInfo":[
                {
                    "startUnit":11,
                    "rooms":"在线教学",
                    "weekDay":7,
                    "weekState":"01111111111111111000000000000000000000000000000000000",
                    "weekStateDigest":"1-16",
                    "endUnit":13
                },
                {
                    "startUnit":6,
                    "rooms":"HGX507",
                    "weekDay":5,
                    "weekState":"01111111111111111000000000000000000000000000000000000",
                    "weekStateDigest":"1-16",
                    "endUnit":10
                }
            ],
            "isAPlus":true,
            "name":"数学分析BII",
            "examFormName":"闭卷",
            "examTime":"2025-06-13 15:30-17:30 第17周 星期五"
        }
        '''

        lessonJSON = json.loads(lessonJSONString)

        course = Course.fromJSON(lessonJSON)
        ```
        """

        # 如果这节课已经创建过了，就直接返回那个已创建的
        if lessonJSON["id"] in cls.courses:
            return cls.courses[lessonJSON["id"]]

        attributes = {}

        attributes["arrangements"] = list(map(Arrangement.fromJSON, lessonJSON["arrangeInfo"]))
        attributes["courseCode"] = lessonJSON["code"]
        attributes["courseId"] = str(lessonJSON["courseId"])
        attributes["courseName"] = lessonJSON["name"]
        attributes["courseNo"] = lessonJSON["no"]
        attributes["examTimeString"] = lessonJSON["examTime"]
        attributes["id"] = str(lessonJSON["id"])

        # 直接赋值那些不用变的项目
        for name in cls.unchangedJSONKeys:
            attributes[name] = lessonJSON[name]

        # 创建并储存、返回实例
        course = cls(**attributes)
        cls.courses[lessonJSON["id"]] = course
        return course


    def toJSON(self) -> dict[str, object]:
        """
        将当前 `Course` 实例的状态序列化为字典（可直接转换为 JSON 格式）。

        ## 返回

        - `dict[str, object]`：包含课程信息的字典，可以直接被 JSON 序列化。

        ## 注意

        - 该方法将对象的所有相关属性转换为适合 JSON 序列化的格式。
        """

        lessonJSON = {}

        lessonJSON["arrangeInfo"] = list(map(Arrangement.toJSON, self["arrangements"]))
        lessonJSON["code"] = self["courseCode"]
        lessonJSON["courseId"] = int(self["courseId"])
        lessonJSON["examTime"] = self["examTimeString"]
        lessonJSON["name"] = self["courseName"]
        lessonJSON["no"] = self["courseNo"]
        lessonJSON["id"] = int(self["id"])
        lessonJSON["teachers"] = ",".join(self["teacherNames"])

        for name in self.unchangedJSONKeys:
            lessonJSON[name] = self[name]

        return lessonJSON


    @cache
    def is_conflict_with(self, other:"Course") -> bool:
        r"""
        检查当前课程`self`与另一门课程`other`之间是否存在冲突。

        该方法首先会检查所有上课时间安排是否有重叠，如果发现任何时间段存在冲突，则立即返回`True`。

        如果没有发现上课时间的冲突，接着会检查两门课程的期末考试时间是否冲突。

        如果没有时间冲突，则检查两门课程的课程代码是否相同，并据此返回结果。

        ## 参数

        - `other`（`Course`）：另一门需要进行冲突检查的课程对象。

        ## 返回

        - `bool`：如果两门课程在上课时间或期末考试时间中任意一项存在冲突，则返回`True`；否则返回`False`。

        ## 注意

        - 此方法经过`cache`修饰，可以记忆参数与输出，实现性能加速。
        """

        # 检查上课时间是否冲突
        for (selfArrangement, otherArrangement) in product(self["arrangements"], other["arrangements"]):
            if selfArrangement.is_conflict_with(otherArrangement):
                return True

        # 检查期末考试时间是否冲突，或者课程代码是否相同
        return self.examTime.is_conflict_with(other.examTime) or (self["courseCode"] == other["courseCode"])


    @property
    def probability(self) -> float:
        r"""
        目前，如果选了这节课，选上这节课的概率。
        """

        if self.selectCount < self.limitCount:
            return 1
        return self.limitCount / (self.selectCount + 1)


    def matchNo(self, pattern: str) -> bool:
        r"""
        检查`self.courseNo`是否完全匹配`pattern`（正则表达式）。
        """

        return bool(fullmatch(pattern, self["courseNo"]))


    @staticmethod
    def norm(x:float) -> float:
        r"""
        经过纵向缩放的正态分布函数

        `x`越接近 `OPTIMAL_PROPORTION_OF_SELECTION` ，返回值就越大，最大为`1`。

        `SIGMA`指定了正态分布函数的离散程度，即本函数的趋近速度。
        """
        return float(norm.pdf(x, loc = OPTIMAL_PROPORTION_OF_SELECTION, scale = SIGMA) / norm.pdf(0))



if __name__ == "__main__":
    import json

    from src.util import timer

    Course.lessonId2Counts = {'737991':{"sc":51,"lc":100},'739850':{"sc":101,"lc":145},'739778':{"sc":5,"lc":15},'740444':{"sc":35,"lc":35},'738278':{"sc":28,"lc":28},'739951':{"sc":86,"lc":95},'738211':{"sc":118,"lc":118},'742339':{"sc":150,"lc":150},'738768':{"sc":51,"lc":95},'738891':{"sc":25,"lc":25},'738890':{"sc":2,"lc":25},'738892':{"sc":25,"lc":25},'738889':{"sc":22,"lc":25},'740351':{"sc":30,"lc":30},'740352':{"sc":24,"lc":30},'740349':{"sc":41,"lc":41},'740350':{"sc":30,"lc":41},'738893':{"sc":120,"lc":120},'738803':{"sc":148,"lc":150},'738802':{"sc":130,"lc":130},'738801':{"sc":60,"lc":60},'738800':{"sc":130,"lc":130},'737876':{"sc":120,"lc":120},'737875':{"sc":44,"lc":120},'740719':{"sc":38,"lc":39},'738804':{"sc":130,"lc":130},'737990':{"sc":94,"lc":160},'742517':{"sc":2,"lc":18}}

    lessonJSONsString = """
    [{"no":"MATH120017.06","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。","teachDepartName":"航空航天系","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"谢锡麟","weekHour":6.0,"id":737991,"endWeek":16,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":11,"rooms":"在线教学","weekDay":7,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":13},{"startUnit":6,"rooms":"HGX507","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":10}],"isAPlus":true,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"PHYS120003.02","courseTypeName":"文理基础课程","code":"PHYS120003","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"物理学系","textbooks":"","canApplyPnp":false,"credits":3.0,"withdrawable":true,"teachers":"季敏标","weekHour":4.0,"id":739850,"endWeek":18,"courseId":41188,"courseTypeCode":"02","startWeek":1,"period":72,"campusCode":"H","courseTypeId":4,"arrangeInfo":[{"startUnit":1,"rooms":"H2214","weekDay":2,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2},{"startUnit":3,"rooms":"H2214","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":false,"name":"普通物理B","examFormName":"闭卷","examTime":"2025-06-17 08:30-10:30 第18周 星期二"},{"no":"FINE110043.01","courseTypeName":"艺术创作与审美体验","code":"FINE110043","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"艺术教育中心","textbooks":"","canApplyPnp":true,"credits":2.0,"withdrawable":true,"teachers":"白建松","weekHour":2.0,"id":739778,"endWeek":18,"courseId":42309,"courseTypeCode":"06_01_05_06","startWeek":1,"period":36,"campusCode":"H","courseTypeId":93,"arrangeInfo":[{"startUnit":8,"rooms":"H6206","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":9}],"isAPlus":false,"name":"数码艺术设计基础","examFormName":"其他","examTime":""},{"no":"ENGL110045.04","courseTypeName":"学术英语课程","code":"ENGL110045","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"校级精品课程","teachDepartName":"大学英语教学部","textbooks":"","canApplyPnp":true,"credits":2.0,"withdrawable":true,"teachers":"贺灿文","weekHour":2.0,"id":740444,"endWeek":16,"courseId":42293,"courseTypeCode":"06_02_03_07","startWeek":1,"period":36,"campusCode":"H","courseTypeId":130,"arrangeInfo":[{"startUnit":1,"rooms":"H2207","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":true,"name":"学术英语（科学技术）","examFormName":"闭卷","examTime":"2025-06-06 18:10-19:10 第16周 星期五"},{"no":"PEDU110131.27","courseTypeName":"通识教育专项教育课程","code":"PEDU110131","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"上海市精品课程 男","teachDepartName":"体育教学部","textbooks":"","canApplyPnp":true,"credits":1.0,"withdrawable":true,"teachers":"黄恩格","weekHour":2.0,"id":738278,"endWeek":18,"courseId":513361,"courseTypeCode":"06_02","startWeek":1,"period":36,"campusCode":"H","courseTypeId":107,"arrangeInfo":[{"startUnit":3,"rooms":"H南区篮球场","weekDay":2,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":false,"name":"篮球（二）","examFormName":"其他","examTime":""},{"no":"PTSS110082.02","courseTypeName":"思政A","code":"PTSS110082","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"思政A组课程","teachDepartName":"马克思主义学院","textbooks":"","canApplyPnp":false,"credits":3.0,"withdrawable":true,"teachers":"金伟","weekHour":3.0,"id":739951,"endWeek":15,"courseId":506240,"courseTypeCode":"01_01_01_01","startWeek":1,"period":54,"campusCode":"H","courseTypeId":58,"arrangeInfo":[{"startUnit":3,"rooms":"HGX307","weekDay":3,"weekState":"01111111111111110000000000000000000000000000000000000","weekStateDigest":"1-15","endUnit":5}],"isAPlus":false,"name":"毛泽东思想和中国特色社会主义理论体系概论","examFormName":"开卷","examTime":"2025-06-07 13:00-15:00 第16周 星期六"},{"no":"NDEC110004.13","courseTypeName":"通识教育课程","code":"NDEC110004","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"军事理论教研室","textbooks":"","canApplyPnp":true,"credits":2.0,"withdrawable":true,"teachers":"郑治龙,邱国","weekHour":2.0,"id":738211,"endWeek":18,"courseId":506637,"courseTypeCode":"01","startWeek":1,"period":36,"campusCode":"H","courseTypeId":2,"arrangeInfo":[{"startUnit":11,"rooms":"H3206","weekDay":4,"weekState":"01111111100000000000000000000000000000000000000000000","weekStateDigest":"1-8","endUnit":12},{"startUnit":11,"rooms":"H3206","weekDay":4,"weekState":"00000000011111111000000000000000000000000000000000000","weekStateDigest":"9-16","endUnit":12}],"isAPlus":false,"name":"军事理论","examFormName":"开卷","examTime":"2025-06-09 19:00-21:00 第17周 星期一"},{"no":"PTSS110080.02","courseTypeName":"思政B","code":"PTSS110080","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"马克思主义学院","textbooks":"","canApplyPnp":false,"credits":2.0,"withdrawable":true,"teachers":"梁君思","weekHour":2.0,"id":742339,"endWeek":18,"courseId":505705,"courseTypeCode":"01_01_01_02","startWeek":1,"period":36,"campusCode":"H","courseTypeId":59,"arrangeInfo":[{"startUnit":6,"rooms":"H2220","weekDay":3,"weekState":"01111111111111110000000000000000000000000000000000000","weekStateDigest":"1-15","endUnit":7}],"isAPlus":false,"name":"中国共产党历史","examFormName":"论文","examTime":""},{"no":"COMP130135.02","courseTypeName":"专业教育课程","code":"COMP130135","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":2.0,"withdrawable":true,"teachers":"刘卉","weekHour":2.0,"id":738768,"endWeek":18,"courseId":488809,"courseTypeCode":"03","startWeek":1,"period":36,"campusCode":"H","courseTypeId":3,"arrangeInfo":[{"startUnit":6,"rooms":"H逸夫楼305,H逸夫楼302","weekDay":4,"weekState":"00101010101010101000000000000000000000000000000000000","weekStateDigest":"2-16双","endUnit":7},{"startUnit":6,"rooms":"HGX507","weekDay":4,"weekState":"01010101010101010000000000000000000000000000000000000","weekStateDigest":"1-15单","endUnit":7}],"isAPlus":false,"name":"面向对象程序设计","examFormName":"闭卷","examTime":"2025-06-18 08:30-10:30 第18周 星期三"},{"no":"MATH120015.03","courseTypeName":"数学类基础课程","code":"MATH120015","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":5.0,"withdrawable":true,"teachers":"吴昊,SHUANGJIAN ZHANG（张霜剑）","weekHour":6.0,"id":738891,"endWeek":18,"courseId":42994,"courseTypeCode":"02_04","startWeek":1,"period":108,"campusCode":"H","courseTypeId":17,"arrangeInfo":[{"startUnit":3,"rooms":"HGX509","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":11,"rooms":"HGX501","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":12},{"startUnit":3,"rooms":"HGX509","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":true,"name":"数学分析AⅡ","examFormName":"闭卷","examTime":"2025-06-12 08:30-10:30 第17周 星期四"},{"no":"MATH120015.02","courseTypeName":"数学类基础课程","code":"MATH120015","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"国家级精品课程","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":5.0,"withdrawable":true,"teachers":"梁振国,王聪","weekHour":6.0,"id":738890,"endWeek":18,"courseId":42994,"courseTypeCode":"02_04","startWeek":1,"period":108,"campusCode":"H","courseTypeId":17,"arrangeInfo":[{"startUnit":13,"rooms":"HGX502","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":14},{"startUnit":3,"rooms":"HGX510","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"HGX510","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":true,"name":"数学分析AⅡ","examFormName":"闭卷","examTime":"2025-06-12 08:30-10:30 第17周 星期四"},{"no":"MATH120015.04","courseTypeName":"数学类基础课程","code":"MATH120015","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":5.0,"withdrawable":true,"teachers":"吴昊,SHUANGJIAN ZHANG（张霜剑）","weekHour":6.0,"id":738892,"endWeek":18,"courseId":42994,"courseTypeCode":"02_04","startWeek":1,"period":108,"campusCode":"H","courseTypeId":17,"arrangeInfo":[{"startUnit":3,"rooms":"HGX509","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"HGX509","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":13,"rooms":"HGX501","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":14}],"isAPlus":true,"name":"数学分析AⅡ","examFormName":"闭卷","examTime":"2025-06-12 08:30-10:30 第17周 星期四"},{"no":"MATH120015.01","courseTypeName":"数学类基础课程","code":"MATH120015","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"国家级精品课程","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":5.0,"withdrawable":true,"teachers":"梁振国,王聪","weekHour":6.0,"id":738889,"endWeek":18,"courseId":42994,"courseTypeCode":"02_04","startWeek":1,"period":108,"campusCode":"H","courseTypeId":17,"arrangeInfo":[{"startUnit":11,"rooms":"HGX502","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":12},{"startUnit":3,"rooms":"HGX510","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"HGX510","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":true,"name":"数学分析AⅡ","examFormName":"闭卷","examTime":"2025-06-12 08:30-10:30 第17周 星期四"},{"no":"MATH120015h.03","courseTypeName":"荣誉课程","code":"MATH120015h","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"英才试验班","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":6.0,"withdrawable":true,"teachers":"严金海,王玥","weekHour":7.0,"id":740351,"endWeek":18,"courseId":519213,"courseTypeCode":"009990","startWeek":1,"period":126,"campusCode":"H","courseTypeId":2342,"arrangeInfo":[{"startUnit":11,"rooms":"HGX402","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":12},{"startUnit":1,"rooms":"H3205","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2},{"startUnit":3,"rooms":"H3205","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":5}],"isAPlus":true,"name":"数学分析AⅡ(H)","examFormName":"闭卷","examTime":"2025-06-12 08:30-11:30 第17周 星期四"},{"no":"MATH120015h.04","courseTypeName":"荣誉课程","code":"MATH120015h","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"英才试验班","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":6.0,"withdrawable":true,"teachers":"严金海,王玥","weekHour":7.0,"id":740352,"endWeek":18,"courseId":519213,"courseTypeCode":"009990","startWeek":1,"period":126,"campusCode":"H","courseTypeId":2342,"arrangeInfo":[{"startUnit":1,"rooms":"H3205","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2},{"startUnit":3,"rooms":"H3205","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":5},{"startUnit":13,"rooms":"HGX402","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":14}],"isAPlus":true,"name":"数学分析AⅡ(H)","examFormName":"闭卷","examTime":"2025-06-12 08:30-11:30 第17周 星期四"},{"no":"MATH120015h.01","courseTypeName":"荣誉课程","code":"MATH120015h","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"英才试验班","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":6.0,"withdrawable":true,"teachers":"楼红卫,李颖洲,印佳","weekHour":7.0,"id":740349,"endWeek":16,"courseId":519213,"courseTypeCode":"009990","startWeek":1,"period":126,"campusCode":"H","courseTypeId":2342,"arrangeInfo":[{"startUnit":11,"rooms":"HGX401","weekDay":4,"weekState":"01011111111111111000000000000000000000000000000000000","weekStateDigest":"1-3单,4-16","endUnit":12},{"startUnit":3,"rooms":"HGX410","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"HGX410","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":5},{"startUnit":11,"rooms":"HGX401","weekDay":4,"weekState":"00100000000000000000000000000000000000000000000000000","weekStateDigest":"2","endUnit":12}],"isAPlus":true,"name":"数学分析AⅡ(H)","examFormName":"闭卷","examTime":"2025-06-12 08:30-11:30 第17周 星期四"},{"no":"MATH120015h.02","courseTypeName":"荣誉课程","code":"MATH120015h","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"英才试验班","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":true,"credits":6.0,"withdrawable":true,"teachers":"楼红卫,李颖洲,印佳","weekHour":7.0,"id":740350,"endWeek":16,"courseId":519213,"courseTypeCode":"009990","startWeek":1,"period":126,"campusCode":"H","courseTypeId":2342,"arrangeInfo":[{"startUnit":3,"rooms":"HGX410","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"HGX410","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":5},{"startUnit":13,"rooms":"HGX401","weekDay":4,"weekState":"01011111111111111000000000000000000000000000000000000","weekStateDigest":"1-3单,4-16","endUnit":14},{"startUnit":13,"rooms":"HGX401","weekDay":4,"weekState":"00100000000000000000000000000000000000000000000000000","weekStateDigest":"2","endUnit":14}],"isAPlus":true,"name":"数学分析AⅡ(H)","examFormName":"闭卷","examTime":"2025-06-12 08:30-11:30 第17周 星期四"},{"no":"MATH120017.08","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"数学科学学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"刘进","weekHour":6.0,"id":738893,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":1,"rooms":"H2214","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2},{"startUnit":3,"rooms":"H2214","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":1,"rooms":"H2214","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.04","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"王勇","weekHour":6.0,"id":738803,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":6,"rooms":"H2115","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":3,"rooms":"H2115","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":1,"rooms":"H2115","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.03","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"郭跃飞","weekHour":6.0,"id":738802,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":3,"rooms":"H3109","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":6,"rooms":"H3109","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":1,"rooms":"H3109","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.02","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"张守志","weekHour":6.0,"id":738801,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":6,"rooms":"H6112","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":3,"rooms":"H6112","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":1,"rooms":"H6112","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.01","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"张巍","weekHour":6.0,"id":738800,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":3,"rooms":"H3308","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":6,"rooms":"H3308","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":1,"rooms":"H3308","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.11","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"管理学院开设","teachDepartName":"管理学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"严金海","weekHour":6.0,"id":737876,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":3,"rooms":"H3108","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"H3108","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":1,"rooms":"H3108","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-20 08:30-10:30 第18周 星期五"},{"no":"MATH120017.09","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"管理学院开设","teachDepartName":"管理学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"黄昭波","weekHour":6.0,"id":737875,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":1,"rooms":"H3106","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2},{"startUnit":3,"rooms":"H3106","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":3,"rooms":"H3106","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-20 08:30-10:30 第18周 星期五"},{"no":"MATH120017.10","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"UIPE全英语课程","teachDepartName":"经济学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"吴鹏","weekHour":6.0,"id":740719,"endWeek":16,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":6,"rooms":"H6505","weekDay":4,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":11,"rooms":"H6505","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":12},{"startUnit":9,"rooms":"H6505","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":10}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-19 13:00-15:00 第18周 星期四"},{"no":"MATH120017.07","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"","teachDepartName":"计算机科学技术学院","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"许扬","weekHour":6.0,"id":738804,"endWeek":18,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":6,"rooms":"H3406","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":3,"rooms":"H3406","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":4},{"startUnit":1,"rooms":"H3406","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":2}],"isAPlus":false,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017.05","courseTypeName":"经管类I组","code":"MATH120017","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。","teachDepartName":"航空航天系","textbooks":"","canApplyPnp":false,"credits":5.0,"withdrawable":true,"teachers":"谢锡麟","weekHour":6.0,"id":737990,"endWeek":16,"courseId":42996,"courseTypeCode":"02_03_01","startWeek":1,"period":108,"campusCode":"H","courseTypeId":113,"arrangeInfo":[{"startUnit":6,"rooms":"H2220","weekDay":1,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":7},{"startUnit":11,"rooms":"在线教学","weekDay":7,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":13},{"startUnit":3,"rooms":"H2220","weekDay":3,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":5}],"isAPlus":true,"name":"数学分析BII","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"},{"no":"MATH120017h.01","courseTypeName":"大类基础课程","code":"MATH120017h","campusName":"邯郸校区","scheduled":true,"hasTextBook":false,"remark":"递进性/混合式教学；国家一流线下课程；在线资源：B站，账号：力学数学-谢锡麟。荣誉课程不开放第三轮选课。","teachDepartName":"航空航天系","textbooks":"","canApplyPnp":true,"credits":6.0,"withdrawable":true,"teachers":"谢锡麟","weekHour":10.0,"id":742517,"endWeek":16,"courseId":519678,"courseTypeCode":"02_2","startWeek":1,"period":180,"campusCode":"H","courseTypeId":1490,"arrangeInfo":[{"startUnit":11,"rooms":"HGX301","weekDay":2,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":12},{"startUnit":6,"rooms":"HGX507","weekDay":5,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":10},{"startUnit":11,"rooms":"在线教学","weekDay":7,"weekState":"01111111111111111000000000000000000000000000000000000","weekStateDigest":"1-16","endUnit":13}],"isAPlus":true,"name":"数学分析BⅡ（H）","examFormName":"闭卷","examTime":"2025-06-13 15:30-17:30 第17周 星期五"}]
    """

    timer.reset()
    lessonJSONs = json.loads(lessonJSONsString)
    # print(timer.read(ndigits = 6))

    courses = []
    timer.reset()
    for lessonJSON in lessonJSONs:
        courses.append(Course.fromJSON(lessonJSON))
    print(timer.read(ndigits = 6))

    for index in range(28):
        print(courses[0].is_conflict_with(courses[index]))
