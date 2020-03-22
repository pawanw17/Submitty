from .base_testcase import BaseTestCase
import requests
import json
import time

class TestAccessibility(BaseTestCase):
    """
    Test cases revolving around the logging in functionality of the site
    """
    def __init__(self, testname):
        super().__init__(testname, log_in=False)

    course_url = ''

    def test_w3_validator(self):
        t0 = time.time()
        new_baseline = False
        # new_baseline = True # Uncomment this line if you want to generate a new baseline

        self.course_url = f"{self.TEST_URL}/{self.get_current_semester()}/sample"

        if new_baseline:
            baseline = {}
        else:
            with open('/'.join(__file__.split('/')[:-1])+'/accessibility_baseline.json') as f:
                baseline = json.load(f)

        foundError = unCheck(self, baseline, new_baseline)

        if new_baseline:
            with open('/'.join(__file__.split('/')[:-1])+'/accessibility_baseline.json', 'w') as file:
                json.dump(baseline, file, ensure_ascii=False, indent=4)


        t1 = time.time()
        print(f'This test took {t1-t0}s to run')
        self.assertEqual(foundError, False)



# The goal of this function is to remove urls that are different but act in the same way
# An example would be we dont want to check every post on the forum, so remove all but 1 post
def urlInUrls(self, new_url, urls):
    for url in urls:
        tmp_new_url = new_url

        if tmp_new_url.startswith(self.course_url+'/forum/threads'):
            tmp_new_url = self.course_url+'/forum'

        if tmp_new_url == url:
            return True


def runCheck(self, baseline, make_new_baseline=False):
    self.log_in(user_id='instructor', user_password='instructor')
    foundError = False
    urls = []
    urls_to_check = [self.TEST_URL+'/home']
    while urls_to_check:
        url = urls_to_check.pop()
        if urlInUrls(self, url, urls):
            continue

        print(url)
        self.driver.get(url)
        urls.append(url)

        if make_new_baseline:
            genBaseline(self, url, baseline)
        else:
            foundError = validatePage(self, url, baseline) or foundError

        new_pages = self.driver.find_elements_by_xpath("//a[@href]")
        print("\n\n\nNEW PAGES FOR", url)
        for page in new_pages:
            href = page.get_attribute("href")
            print(href)
            if not href.startswith(self.course_url):
                continue
            urls_to_check.append(page.get_attribute("href").split('?')[0].split('#')[0])

    return foundError



def validatePage(self, url, baseline):
    foundError = False

    payload = self.driver.page_source
    print(self.driver.page_source)
    headers = {
      'Content-Type': 'text/html; charset=utf-8'
    }
    response = requests.request("POST", "https://validator.w3.org/nu/?out=json", headers=headers, data = payload.encode('utf-8'))

    for error in response.json()['messages']:
        # For some reason the test fails to detect this even though when you actually look at the rendered
        # pages this error is not there. So therefore the test is set to just ignore this error.
        if error['message'].startswith("Start tag seen without seeing a doctype first"):
            continue

        if error['message'] not in baseline[url]:
            error['url'] = url
            print(json.dumps(error, indent=4, sort_keys=True))
            foundError = True

    # self.assertEqual(foundError, False)
    return foundError



def genBaseline(self, url, baseline):
    payload = self.driver.page_source
    headers = {
      'Content-Type': 'text/html; charset=utf-8'
    }
    response = requests.request("POST", "https://validator.w3.org/nu/?out=json", headers=headers, data = payload.encode('utf-8'))

    baseline[url] = {}
    for error in response.json()['messages']:
        # For some reason the test fails to detect this even though when you actually look at the rendered
        # pages this error is not there. So therefore the test is set to just ignore this error.
        if error['message'].startswith("Start tag seen without seeing a doctype first"):
            continue

        if error['message'] not in baseline[url]:
            baseline[url][error['message']] = error
