from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import ddddocr
import cv2
import time
import numpy as np

class JKYZ_cheat:
    def __init__(self, username, password):

        #隐藏痕迹
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--disable-blink-features=AutomationControlled')
        #options.add_argument('--user-data-dir=')
        # 需要修改对应browser drive的路径
        self.browser = webdriver.Chrome("C:/Program Files/Google/Chrome/Application/chromedriver.exe", options=options)
        self.user = username
        self.passw = password

    def login_from_cookie(self):
        #根据cookie信息登陆，一般不用
        self.browser.get('https://hk.sz.gov.cn:8118')
        for c in self.cookies:
            self.browser.add_cookie(c)
        self.browser.refresh()
        WebDriverWait(self.browser, 2, 0.1).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[@id='winOrderNotice']/div[@class='flexbox btngroup']/div[@class='flex1']/button")))
        self.browser.find_element(By.XPATH, "/html/body/div[@id='winOrderNotice']/div[@class='flexbox btngroup']/div[@class='flex1']/button").click()


    def isClassPresent(self, name, ret=False):
        try:
            result = self.browser.find_element(By.CLASS_NAME,name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    def refresh_yzm(self):
        #刷新验证码
        element = self.browser.find_element_by_id('img_verify')
        element.click()

    def cutyzm(self, YZM_path):
        #验证码截取
        self.browser.get_screenshot_as_file('spider/screenshot.png')
        element = self.browser.find_element_by_id('img_verify')
        element.screenshot(YZM_path)


    def recogyzm(self, path):
        #验证码识别
        ocr=ddddocr.DdddOcr()
        img=cv2.imread(path)
        img2 = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img2 = cv2.inRange(img2, lowerb=107, upperb=255)
        _,img_bytes=cv2.imencode('.png', img2)
        img_bytes=img_bytes.tobytes()
        res=ocr.classification(img_bytes)
        return res


    def login(self):
        url="https://hk.sz.gov.cn:8118"
        self.browser.get(url)
        #self.browser.add_cookie(self.cookies[0])
        self.browser.find_element(By.XPATH, "/html/body/div[@id='winLoginNotice']/div[@class='flexbox btngroup']/div[@class='flex1']/button").click()
        zhengjianleixing=Select(self.browser.find_element_by_id('select_certificate'))
        #不是回乡证的话，下面的value要改变。
        zhengjianleixing.select_by_value('4')
        zhengjianhaoma=self.browser.find_element_by_id('input_idCardNo')
        zhengjianhaoma.send_keys(self.user)#需要在此输入通行证号码
        mima=self.browser.find_element_by_id('input_pwd')
        mima.send_keys(self.passw)#需要在此输入密码

        while True:
            #验证码截取
            self.cutyzm('spider/code.png')
            #验证码识别
            res = self.recogyzm("spider/code.png")
            res = res.replace('o', '0')
            print(res)
            #输入验证码
            yanzhengma=self.browser.find_element_by_id('input_verifyCode')
            yanzhengma.send_keys(res)
            time.sleep(3)
            self.browser.find_element_by_id('btn_login').click()

            try:
                WebDriverWait(self.browser, 2, 0.1).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[@id='winOrderNotice']/div[@class='flexbox btngroup']/div[@class='flex1']/button")))
                self.browser.find_element(By.XPATH, "/html/body/div[@id='winOrderNotice']/div[@class='flexbox btngroup']/div[@class='flex1']/button").click()
                break
            except:
                time.sleep(1)
                yanzhengma.clear()
                self.refresh_yzm()
                pass

    def get_dx(self, img_path):
        #根据图片，算出滑块需要的步长
        img = cv2.imread(img_path)
        canny = cv2.Canny(img, 300, 300)
        contours, hierarchy = cv2.findContours(canny, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        dx, dy = 0, 0
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if (x > 50) and (w > 40) and (h > 40):
                dx = x
                dy = y
                dw = w
                dh = h
        cv2.rectangle(img, (dx, dy), (dx + dw, dy + dh), (0, 0, 255), 2)
        cv2.imwrite('spider/test.png', img)
        return dx, dy

    def getTrack(self, distance):
        #计算轨迹走法
        ds = distance - 38  # 38是滑块位置
        # 分4次走完。
        dx_1 = round(ds * 1 / 5)
        dx_2 = dx_1 * 3
        dx_3 = dx_1 + np.random.randint(-10, 10)
        dx_4 = ds - dx_1 - dx_2 - dx_3
        track = [dx_1, dx_2, dx_3, dx_4]
        return track



    def QiangPiao(self, QP_time):
        #到时间点进去，直到输入验证码的页面。
        self.browser.set_page_load_timeout(500)
        self.browser.set_script_timeout(500)
        c = self.browser.get_cookies()
        cookies = {}
        for cookie in c:
            cookies[cookie['name']] = cookie['value']
        print(cookies)
        while True:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            time.sleep(0.1)
            # print(current_time)
            if current_time == QP_time:
                print(current_time)
                #time.sleep(0.5)
                # url = "https://hk.sz.gov.cn:8118/passInfo/detail"
                # self.browser.get(url)
                self.browser.find_element_by_id('a_canBookHotel').click()
                element = WebDriverWait(self.browser, 300, 0.1).until(
                    EC.presence_of_element_located((By.ID, "divSzArea"))
                )
                #最后一天至倒数第二天。
                for i in [7,6,5,4,3,2]:
                    try:
                        yuyue = self.browser.find_element(By.XPATH,
                                                          "/html/body/div[@class='layout_body']/div[@class='tzlist tongguanlist yuyuelist']/div[@id='divSzArea']/section[@class='card_info'][" + str(i) + "]/div[@class='flexbox']/div[3]/div/a[@class='orange button']")

                        yuyue.click()
                        break
                    except:
                        pass
                print(current_time)
                break

        WebDriverWait(self.browser, 200, 0.1).until(EC.visibility_of_element_located((By.ID, 'TencentCaptcha')))
        # 判断某个元素是否被添加到了dom里并且可见
        self.browser.get_screenshot_as_file('spider/screenshot_2.png')
        element = self.browser.find_element(By.ID, 'TencentCaptcha')
        element.click()
        # 由于最后阶段的验证码更新了，无法破解，所以只能手动解决并且确认。
        # time.sleep(0.2)
        # #截图验证码，识别。
        # self.browser.switch_to.frame("tcaptcha_iframe")
        # ele = self.browser.find_element(By.ID, 'slideBg')
        # ele.screenshot('spider/yzm_code2.png')
        # # 3. 拉动滑块， 模拟人的运动。
        # element = self.browser.find_element(By.ID, 'tcaptcha_drag_thumb')
        # dx, dy = self.get_dx('spider/yzm_code2.png')
        # track = self.getTrack(dx)
        # move = webdriver.ActionChains(self.browser)
        # # 点击，准备拖拽
        # move.click_and_hold(element).perform()
        # for x in track:
        #     move.move_by_offset(xoffset=x, yoffset=0).perform()
        #     time.sleep(0.2)
        # move.release().perform()
        # time.sleep(0.2)
        # #brow_user1.browser.switch_to.default_content()
        # self.browser.find_element(By.ID, 'btn_confirmOrder').click()
        # print('抢票成功')

#回乡证号码填写。
brow_user1 = JKYZ_cheat(username='passport', password='password')
brow_user1.login()
#brow_user1.login_from_cookie()
time.sleep(3)
#如果网络好，可以尝试准点入，注意更新系统时间，这个是通过主机上的时间来判断的。
brow_user1.QiangPiao(QP_time="10:00:01")  




