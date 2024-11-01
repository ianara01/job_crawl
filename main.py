# job_crawler.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import pandas as pd

def setup_chrome_driver(headless=False, download_path=None):
    """
    Chrome WebDriver를 자동으로 설정하는 함수
    
    Args:
        headless (bool): 헤드리스 모드 실행 여부
        download_path (str): 파일 다운로드 경로 (선택사항)
    
    Returns:
        webdriver: 설정된 Chrome WebDriver 인스턴스
    """
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Chrome 옵션 설정
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')  # 헤드리스 모드
        
        # 기본 옵션 설정
        chrome_options.add_argument('--start-maximized')  # 창 최대화
        chrome_options.add_argument('--disable-notifications')  # 알림 비활성화
        chrome_options.add_argument('--no-sandbox')  # 샌드박스 비활성화
        chrome_options.add_argument('--disable-dev-shm-usage')  # 공유 메모리 사용 비활성화
        chrome_options.add_argument('--disable-gpu')  # 브라우저 크래시 방지
        chrome_options.add_argument('--disable-software-rasterizer')
        
        # 불필요한 로그 제거
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 다운로드 경로 설정 (지정된 경우)
        if download_path:
            prefs = {
                "download.default_directory": download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
        
        # Chrome 드라이버 자동 설치 및 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 페이지 로드 타임아웃 설정
        driver.set_page_load_timeout(30)
        
        logger.info("Chrome WebDriver가 성공적으로 설정되었습니다.")
        return driver
    
    except Exception as e:
        logger.error(f"Chrome WebDriver 설정 중 오류 발생: {str(e)}")
        raise

def crawl_job_data(search_keyword):
    """
    JobKorea에서 특정 검색어로 검색하고 결과 데이터를 크롤링하는 함수
    
    Args:
        search_keyword (str): 검색어
    
    Returns:
        DataFrame: 크롤링된 데이터
    """
    # 드라이버 설정
    driver = setup_chrome_driver()
    
    try:
        # JobKorea 웹사이트 접속
        driver.get("https://www.jobkorea.co.kr/")
        
        # 검색창 클릭
        element = driver.find_element(By.XPATH, '//*[@id="stext"]')
        element.click()
        
        # 검색어 입력
        element.send_keys(search_keyword)
        
        # 검색 버튼 클릭
        search_button = driver.find_element(By.XPATH, '//*[@id="common_search_btn"]')
        search_button.click()
        
        # 검색 결과에서 데이터 수집
        data_elements = driver.find_elements(By.CLASS_NAME, "list-item")
        
        # 데이터 정리
        crawling_data = []
        for data in data_elements:
            company_name = data.text.split("\n")[0]
            job_info = "_".join(data.text.split("\n")[1:])
            crawling_data.append([company_name, job_info])
        
        # DataFrame 생성
        df = pd.DataFrame(crawling_data, columns=["Company", "Job_Find_Info"])
        
        # 데이터 CSV 파일로 저장
        df.to_csv("today_jobinfo1.csv", index=False, encoding='utf-8-sig')
        print("CSV 파일이 성공적으로 저장되었습니다: today_jobinfo1.csv")
        
        return df
    
    except Exception as e:
        print(f"크롤링 중 오류 발생: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # 패키지 설치 안내
    print("다음 패키지들이 필요합니다:")
    print("pip install selenium webdriver-manager pandas")
    
    # 크롤링 실행
    search_keyword = "파이썬 백엔드"  # 검색어 설정
    df = crawl_job_data(search_keyword)
    
    if df is not None:
        print("크롤링이 성공적으로 완료되었습니다.")
    else:
        print("크롤링에 실패했습니다.")
