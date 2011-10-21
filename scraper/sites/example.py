import re
from jobscraper import parser

def parse_date(datestring):
    match = re.search('(\d\d)-(\d\d)-(\d\d\d\d)', datestring)
    return "%s-%s-%sT00:00:00Z" % (match.group(3), match.group(2), match.group(1))
    
def parse_min_salary(salary_str):
    salary = parser.salary_parser(salary_str)
    return salary[0] if salary else None

def parse_max_salary(salary_str):
    salary = parser.salary_parser(salary_str)
    return salary[1] if salary and len(salary) > 1 else None
    
def parse_min_experience(exp_str):
    exp = parser.experience_parser(exp_str)
    return exp[0] if exp else None

def parse_max_experience(exp_str):
    exp = parser.experience_parser(exp_str)
    return exp[1] if exp and len(exp) > 1 else None

def parse_hours(hours_str):
    return parser.hours_parser(hours_str)

conf = {
    'scraper' : {
        'fields': {
            'title': {'xpath': '//h1[@class="heading-a"]'},
            'date': {'xpath': "//td[@id='prefijoFecha']", 'transf': [parse_date]},
            'company': {'xpath': "//td[@id='prefijoEmpresa']"},
            'reference': {'xpath': "//div[@class='reference']"},
            'country': {'xpath': "//td[@id='prefijoPais']"},
            'province': {'xpath': "//a[@id='prefijoProvincia']"},
            'municipality': {'xpath': "//td[@id='prefijoPoblacion']"},
            'description': {'xpath': "//td[@id='prefijoDescripcion1']"},
            'sectors': {'xpath': "//table[@class='DatosTabulados' and position()=3]//tr/td/table//tr/td"},
            'vacancies': {'xpath': "//td[@id='prefijoVacantes']"},
            'requirements': {'xpath': "//td[@id='prefijoReqMinimos']"},
            'studies': {'xpath': "//td[@id='prefijoEstMin']"},
            'experience': {'xpath': "//td[@id='prefijoExpMin']"},
            'min_experience': {'xpath': "//td[@id='prefijoExpMin']", 'transf': [parse_min_experience]},
            'max_experience': {'xpath': "//td[@id='prefijoExpMin']", 'transf': [parse_max_experience]},
            'desired': {'xpath': "//td[@id='prefijoReqDeseados']"},
            'residence': {'xpath': "//table[@class='DatosTabulados' and position()=4]//tr[3]/td[not(@id) and position()=2]"},
            'salary': {'xpath': "//td[@id='prefijoSalario']"},
            'min_salary': {'xpath': "//td[@id='prefijoSalario']", 'transf': [parse_min_salary]},
            'max_salary': {'xpath': "//td[@id='prefijoSalario']", 'transf': [parse_max_salary]},
            'contract': {'xpath': "//td[@id='prefijoContrato']"},
            'duration': {'xpath': "//td[@id='prefijoDuracion']"},
            'hours': {'xpath': "//td[@id='prefijoJornada']", 'transf': [parse_hours]},
            'category': {'xpath': "//a[@id='prefijoCat']"},
            'offered': {'xpath': "//table[@class='DatosTabulados' and position()=6]//tr/td"},
		},
        'request_wait' : 0,
    },

    'crawler'  : {
        'start_url' : 'http://www.example.net/ofertas-trabajo',
        'elements_xpath' : '//a[starts-with(@id, "table_results_offer")]/@href',
        'elements_transf' : lambda x: re.sub('^//', 'http://', x),
        'nextpage_url_xpath' : 'string(//li[@class="next"]/a/@href)',
        'nextpage_url_transf' : lambda x: "http://www.example.net" + x,
        'request_wait' : 2
    }
}
