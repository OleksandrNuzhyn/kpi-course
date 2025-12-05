import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

BASE_URL = "http://localhost:5173"
STUDENT_EMAIL = "student.ivanenko@email.ua"
TEACHER_EMAIL = "teacher.pavlenko@email.ua"
PASSWORD = "password123#"


class EkafedraSeleniumTests(unittest.TestCase):
    def setUp(self): 
        options = webdriver.EdgeOptions()
        self.driver = webdriver.Edge(options=options)
        self.driver.implicitly_wait(5)
        self.driver.maximize_window()

    def tearDown(self):
        self.driver.quit()

    # Перевірка успішного входу та виходу з системи
    def test_successful_login_and_logout(self):
        self.driver.get(f"{BASE_URL}/login")

        self.driver.find_element(By.ID, "email").send_keys(STUDENT_EMAIL)
        self.driver.find_element(By.ID, "password").send_keys(PASSWORD)

        login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        try:
            logout_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Logout')]"))
            )
        except TimeoutException:
            self.fail("Кнопка 'Logout' не з'явилася після логіну.")

        self.assertTrue(logout_button.is_displayed(), "Кнопка 'Logout' не відображається на сторінці.")

        logout_button.click()

        WebDriverWait(self.driver, 10).until(EC.url_contains("/login"))

        self.assertIn("/login", self.driver.current_url, "Не відбулося перенаправлення на сторінку логіну після виходу.")

    # Перевірка подачі заявки студентом на вільну тему
    def test_student_submits_application_for_topic(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "email").send_keys(STUDENT_EMAIL)
        self.driver.find_element(By.ID, "password").send_keys(PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        my_streams_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "My Streams"))
        )
        my_streams_link.click()

        try:
            stream_card = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".bg-white.p-6.rounded-xl"))
            )
            first_stream_link = stream_card.find_element(By.PARTIAL_LINK_TEXT, "View Available Topics")
            first_stream_link.click()
        except TimeoutException:
            self.fail("Не знайдено жодної картки потоку або посилання 'View Available Topics' на сторінці 'My Streams'.")
            
        try:
            apply_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Submit Application"))
            )
            apply_button.click()
            
        except TimeoutException:
            self.fail("Не знайдено кнопки 'Submit Application' для жодної теми.")

        try:
            vision_textarea = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "student_vision"))
            )
            vision_textarea.send_keys("Моє бачення теми, введене автоматичним тестом.")
            
            form = self.driver.find_element(By.XPATH, "//form")
            self.driver.execute_script("arguments[0].requestSubmit();", form)

        except TimeoutException:
            self.fail("Форма подачі заявки (textarea) не з'явилася.")

        try:
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("/my-submissions")
            )
        except TimeoutException:
            with open("submission_failure_page.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.driver.save_screenshot("submission_form_failure.png")
            self.fail("Не відбулося перенаправлення. Перевірте файли submission_failure_page.html та submission_form_failure.png.")

    # Перевірка схвалення заявки студента викладачем
    def test_teacher_approves_submission(self):
        self.driver.get(f"{BASE_URL}/login")
        self.driver.find_element(By.ID, "email").send_keys(TEACHER_EMAIL)
        self.driver.find_element(By.ID, "password").send_keys(PASSWORD)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        received_link = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Received"))
        )
        received_link.click()
        
        topic_containers = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.bg-white.rounded-2xl.shadow-lg"))
        )

        if not topic_containers:
            self.fail("Не знайдено жодної теми на сторінці 'Received Submissions'.")

        approved = False
        for container in topic_containers:
            header = container.find_element(By.CSS_SELECTOR, "button.w-full")
            header.click()
            
            try:
                approve_button = WebDriverWait(container, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.text-green-800"))
                )
                
                self.driver.execute_script("arguments[0].click();", approve_button)
                approved = True
                break

            except TimeoutException:
                continue

        if not approved:
            self.fail("Не знайдено жодної заявки зі статусом 'PENDING' після перевірки всіх тем.")

        try:
            WebDriverWait(container, 10).until(
                EC.presence_of_element_located((By.XPATH, ".//span[contains(text(), 'APPROVED')]"))
            )
        except TimeoutException:
            self.fail("Статус заявки не оновився на 'APPROVED' в межах контейнера теми.")


if __name__ == '__main__':
    unittest.main(verbosity=2)