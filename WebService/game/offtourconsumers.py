import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class GameConsumer(AsyncWebsocketConsumer):

    connected_clients_count = 0
    updating_ball_position = False
    
    game_over_flag = False
    game_winner_local = 0
    
    play_bar1_position = {'x': 0, 'y': 9}
    play_bar2_position = {'x': 0, 'y': -9}
    ball_position = {'x': 0, 'y': 0}
    ball_velocity = {'x': 0.03, 'y': 0.02}  # 공의 속도
    score_player1 = 0
    score_player2 = 0
    
    game_over_score = 3;

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "chat_" + self.room_name

        await (self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ))
        await self.accept() 
        asyncio.create_task(self.ball_position_updater())

    async def disconnect(self, close_code):
        GameConsumer.connected_clients_count -= 1
        await (self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        print(message , " " , self.channel_name)

        # 계산식
        if message == 'a':
            GameConsumer.play_bar1_position['x'] = max(-9,
                                               GameConsumer.play_bar1_position['x'] - 0.4)
        elif message == 'd':
            GameConsumer.play_bar1_position['x'] = min(
                9, GameConsumer.play_bar1_position['x'] + 0.4)
        if message == 'j':
            GameConsumer.play_bar2_position['x'] = max(-9,
                                               GameConsumer.play_bar2_position['x'] - 0.4)
        elif message == 'l':
            GameConsumer.play_bar2_position['x'] = min(
                9, GameConsumer.play_bar2_position['x'] + 0.4)

    async def _update_ball_position(self):
        # 공 위치 업데이트
        GameConsumer.ball_position['x'] += GameConsumer.ball_velocity['x']
        GameConsumer.ball_position['y'] += GameConsumer.ball_velocity['y']

        bar_width = 2  # 예시 값, 실제 바의 가로 길이에 맞게 조정
        ball_radius = 0.5  # 예시 값, 실제 공의 반지름에 맞게 조정

        # # 첫 번째 플레이어 바와 공의 충돌 검사
        if GameConsumer.play_bar1_position['y'] - ball_radius < GameConsumer.ball_position['y'] < GameConsumer.play_bar1_position['y'] + ball_radius \
                and self.play_bar1_position['x'] - bar_width / 2 < self.ball_position['x'] < self.play_bar1_position['x'] + bar_width / 2:
            GameConsumer.ball_velocity['y'] *= -1  # y 방향 반전

        # # 두 번째 플레이어 바와 공의 충돌 검사
        if GameConsumer.play_bar2_position['y'] - ball_radius < GameConsumer.ball_position['y'] < GameConsumer.play_bar2_position['y'] + ball_radius \
                and GameConsumer.play_bar2_position['x'] - bar_width / 2 < GameConsumer.ball_position['x'] < GameConsumer.play_bar2_position['x'] + bar_width / 2:
            GameConsumer.ball_velocity['y'] *= -1  # y 방향 반전

        # 벽과의 충돌 처리
        # up ,down wall collision
        if GameConsumer.ball_position['y'] <= -10 or GameConsumer.ball_position['y'] >= 10:
            # collision on upper side wall, player2 score up
            if GameConsumer.ball_position['y'] > 10:
                GameConsumer.score_player2 += 1
            # collision on bottom side wall,player1 score up
            elif GameConsumer.ball_position['y'] < -10:
                GameConsumer.score_player1 += 1
            # 실점 후 판 재배치
            GameConsumer.ball_position = {'x': 0, 'y': 0}
            GameConsumer.play_bar1_position = {'x': 0, 'y': 9}
            GameConsumer.play_bar2_position = {'x': 0, 'y': -9}
            await asyncio.sleep(2)
        
        if GameConsumer.score_player1 == GameConsumer.game_over_score :
            GameConsumer.game_over_flag = True
            GameConsumer.game_winner_local = 1
            
        if GameConsumer.score_player2 == GameConsumer.game_over_score :
            GameConsumer.game_over_flag = True
            GameConsumer.game_winner_local = 2
        
        # left, right wall collisio
        if GameConsumer.ball_position['x'] <= -10 or GameConsumer.ball_position['x'] >= 10:
            GameConsumer.ball_velocity['x'] *= -1  # x 방향 반전

        # 모든 클라이언트에 변경된 정보 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',  # 호출할 메서드 이름
                'play_bar1_position': GameConsumer.play_bar1_position,
                'play_bar2_position': GameConsumer.play_bar2_position,
                'ball_position': GameConsumer.ball_position,
                'score_player1': GameConsumer.score_player1,
                'score_player2': GameConsumer.score_player2,
                'game_over_flag': GameConsumer.game_over_flag,
                'game_winner': GameConsumer.game_winner_local
            }
        )

    async def ball_position_updater(self):

        while not GameConsumer.game_over_flag:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 50번의 업데이트가 1초 동안 진행됨
        
        GameConsumer.game_over_flag = False
        GameConsumer.connected_clients_count = 0
        GameConsumer.updating_ball_position = False
        GameConsumer.game_over_flag = False
        GameConsumer.game_winner_local = 0
        GameConsumer.play_bar1_position = {'x': 0, 'y': 9}
        GameConsumer.play_bar2_position = {'x': 0, 'y': -9}
        GameConsumer.ball_position = {'x': 0, 'y': 0}
        GameConsumer.ball_velocity = {'x': 0.03, 'y': 0.02}  # 공의 속도
        GameConsumer.score_player1 = 0
        GameConsumer.score_player2 = 0
        GameConsumer.game_over_score = 3;
            

    async def game_update(self, event):
        # 이 메서드는 group_send 호출로 인해 자동으로 실행됩니다.
        await self.send(text_data=json.dumps({
            'play_bar1_position': event['play_bar1_position'],
            'play_bar2_position': event['play_bar2_position'],
            'ball_position': event['ball_position'],
            'score_player1': event['score_player1'],
            'score_player2': event['score_player2'],
            'game_over_flag': event['game_over_flag'],
            'game_winner': event['game_winner']
        }))
