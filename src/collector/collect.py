import os
import pandas as pd
from datetime import datetime

class Collector:
    '''
    데이터 수집하는 수집기 객체
    어떤 거래소에서든 돌아가는 게 목표임
    '''
    def __init__(self):
        self.tmp = None
        self.exchange = None
        self.save_path = ''

    def set_preference(self, preference):
        '''
        어떤 데이터를 어떻게 수집할 건지 정의, 설정하는 함수
        목표 데이터 정보에 대한 메타 정보 포함
        '''
        self.preference = preference
        self.save_path = ''

    def set_exchange(self, exchange):
        '''
        특정 거래소를 지정하고 준비시킴
        수집 직전의 상태로 변경됨
        '''
        self.exchange = exchange
        self.exchange.set_preference(self.preference)

    def execute(self):
        '''
        정의된 데이터를 지정된 거래소에서 수집하는 것을 실행
        거래소에서 조회한 데이터를 받아 로컬에 저장하는 단계
        '''

        data_generator = self.exchange.get_data() # generator

        for data, info in data_generator:
            if self.__save(data, info):
                break

    def execute_update(self):
        pass

    def execute_flush(self):
        pass

    
    def __save_and_check_overlap(self, data, info):
        '''
        거래소에서 받아온 데이터를 직접 저장하는 메서드
        일관된 형식으로 받아서 일관된 형태로 저장하기 때문에 거래소 모듈에서 forming 해야함
        '''

        is_overlap = False
        path = os.path.join(info[0],
                            info[1],
                            info[2],
                            info[3],
                            )

        # 파일이 존재하면 이어 붙이기
        if os.path.exists(f'{path}.csv'):
            df = pd.read_csv(f'{path}.csv', index_col=0)
            df = pd.concat([data, df], ignore_index=True)
        else:
            if not os.path.exists(os.path.split(path)[0]):
                os.makedirs(os.path.split(path)[0])
            df = data
            

        df.to_csv(f'{path}.csv')

        return is_overlap

    # update
    def __update_and_check_overlap(self, data, info):
        '''
        거래소에서 받아온 데이터를 직접 저장하는 메서드
        일관된 형식으로 받아서 일관된 형태로 저장하기 때문에 거래소 모듈에서 forming 해야함
        '''

        is_overlap = False
        path = os.path.join(info[0],
                            info[1],
                            info[2],
                            info[3],
                            )

        # 파일이 존재하면 이어 붙이기
        if os.path.exists(f'{path}.csv'):
            df = pd.read_csv(f'{path}.csv', index_col=0)
            
            # 날짜 중복되면 중지할 준비
            if datetime.strptime(str(df.iloc[-1]['datetime']), '%Y%m%d%H%M%S') > datetime.strptime(str(data.iloc[-1]['datetime']), '%Y%m%d%H%M%S'):
                is_overlap = True
            df = pd.concat([data, df], ignore_index=True)
        else:
            if not os.path.exists(os.path.split(path)[0]):
                os.makedirs(os.path.split(path)[0])
            df = data
            

        df.to_csv(f'{path}.csv')

        return is_overlap

        ###############################
        # self.data_queue
        # path = os.path.join(info[0],
        #                     info[1],
        #                     info[2],
        #                     info[3],
        #                     )

        # if not os.path.exists(os.path.split(path)[0]):
        #     os.makedirs(os.path.split(path)[0])

        # with open(f'{path}.csv', 'w') as f:
        #     f.write(''.join(map(str, data)))

class Runner:
    def __init__(self):
        pass


class Preference:
    '''
    사용자가 수집하려는 데이터 형식
    '''
    def __init__(self, market_type='stock', data_type='cangle', period='1m', items=['005930', '035720', '035420'], range_=['20220103', '20220105']):
        self.market_type = market_type
        self.data_type = data_type
        self.period = period
        self.items = items
        self.range = range_
        # self.~