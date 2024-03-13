import json
import uuid
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):

    play_bar1_position = {'x': 0, 'y': 9}
    play_bar2_position = {'x': 0, 'y': -9}
    ball_position = {'x': 0, 'y': 0}
    ball_velocity = {'x': 0.03, 'y': 0.02}  # 공의 속도
    score_player1 = 0
    score_player2 = 0
		
    async def connect(self):

        # group을 미리 만들거나 특정 닉네임을 기준으로 만드는방식?
        # 그룹에 빈공간이 있는지, 특정 닉네님이 있는지 확인
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "chat_" + self.room_name
        await (self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        ))
        await self.accept()
        asyncio.create_task(self.ball_position_updater())

    async def disconnect(self, close_code):
        await (self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        ))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # 계산식
        if message == 'a':
            # 왼쪽으로 이동할 때는 'x' 좌표를 감소시킵니다.
            self.play_bar1_position['x'] = max(-9,
                                               self.play_bar1_position['x'] - 0.4)
        elif message == 'd':
            # 오른쪽으로 이동할 때는 'x' 좌표를 증가시킵니다.
            self.play_bar1_position['x'] = min(
                9, self.play_bar1_position['x'] + 0.4)

        # 두 번째 플레이어의 바 이동
        if message == 'j':
            # 왼쪽으로 이동할 때는 'x' 좌표를 감소시킵니다.
            self.play_bar2_position['x'] = max(-9,
                                               self.play_bar2_position['x'] - 0.4)
        elif message == 'l':
            # 오른쪽으로 이동할 때는 'x' 좌표를 증가시킵니다.
            self.play_bar2_position['x'] = min(
                9, self.play_bar2_position['x'] + 0.4)

        self._update_ball_position()



    async def _update_ball_position(self):
        # 공 위치 업데이트
        self.ball_position['x'] += self.ball_velocity['x']
        self.ball_position['y'] += self.ball_velocity['y']

        # 바와 공의 충돌 검사
        # 바의 가로 길이 및 공의 크기를 고려해야 함
        bar_width = 2  # 예시 값, 실제 바의 가로 길이에 맞게 조정
        ball_radius = 0.5  # 예시 값, 실제 공의 반지름에 맞게 조정

        # # 첫 번째 플레이어 바와 공의 충돌 검사
        if self.play_bar1_position['y'] - ball_radius < self.ball_position['y'] < self.play_bar1_position['y'] + ball_radius \
                and self.play_bar1_position['x'] - bar_width / 2 < self.ball_position['x'] < self.play_bar1_position['x'] + bar_width / 2:
            self.ball_velocity['y'] *= -1  # y 방향 반전

        # # 두 번째 플레이어 바와 공의 충돌 검사
        if self.play_bar2_position['y'] - ball_radius < self.ball_position['y'] < self.play_bar2_position['y'] + ball_radius \
                and self.play_bar2_position['x'] - bar_width / 2 < self.ball_position['x'] < self.play_bar2_position['x'] + bar_width / 2:
            self.ball_velocity['y'] *= -1  # y 방향 반전

        # 벽과의 충돌 처리
        # up ,down wall collision
        if self.ball_position['y'] <= -10 or self.ball_position['y'] >= 10:
            # collision on upper side wall, player2 score up
            if self.ball_position['y'] > 10:
                self.score_player2 += 1
                await self._reset_ball_and_pause()
            # collision on bottom side wall,player1 score up
            elif self.ball_position['y'] < -10:
                self.score_player1 += 1
                await self._reset_ball_and_pause()
        # left, right wall collision
        if self.ball_position['x'] <= -10 or self.ball_position['x'] >= 10:
            self.ball_velocity['x'] *= -1  # x 방향 반전

        # 모든 클라이언트에 변경된 정보 전송
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',  # 호출할 메서드 이름
                'play_bar1_position': self.play_bar1_position,
                'play_bar2_position': self.play_bar2_position,
                'ball_position': self.ball_position,
                'score_player1': self.score_player1,
                'score_player2': self.score_player2
            }
        )

    async def _reset_ball_and_pause(self):
        # 공의 위치를 중앙으로 초기화
        self.ball_position = {'x': 0, 'y': 0}
        self.play_bar1_position = {'x': 0, 'y': 9}
        self.play_bar2_position = {'x': 0, 'y': -9}

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',  # 호출할 메서드 이름
                'play_bar1_position': self.play_bar1_position,
                'play_bar2_position': self.play_bar2_position,
                'ball_position': self.ball_position,
                'score_player1': self.score_player1,
                'score_player2': self.score_player2
            }
        )
        # 공의 속도를 초기화하거나, 원하는 초기 속도로 설정할 수 있습니다.
        import random
        self.ball_velocity = {'x': random.choice(
            [0.03, -0.02]), 'y': random.choice([0.03, -0.02])}

        # 점수 업데이트 후 1초간 휴식
        # await asyncio.sleep(4)

    async def ball_position_updater(self):
        while True:
            await self._update_ball_position()
            await asyncio.sleep(0.02)  # 1초마다 공 위치 업데이트
            # print(self.ball_position + " " + self.play_bar1_position + " " + self.play_bar2_position);
            dx = self.ball_velocity['x']
            dy = self.ball_velocity['y']
            if dx != 0:
                slope = dy / dx
                print(
                    f"Ball Position: {self.ball_position}, Bar1 Position: {self.play_bar1_position}, Bar2 Position: {self.play_bar2_position}, Slope: {slope}")
            else:
                print(
                    f"Ball Position: {self.ball_position}, Bar1 Position: {self.play_bar1_position}, Bar2 Position: {self.play_bar2_position}, Slope: vertical")

    async def game_update(self, event):
        # 이 메서드는 group_send 호출로 인해 자동으로 실행됩니다.
        # event 매개변수는 group_send 호출 시 전달한 딕셔너리입니다.

        # 클라이언트에게 게임 상태 정보를 전송합니다.
        await self.send(text_data=json.dumps({
            'play_bar1_position': event['play_bar1_position'],
            'play_bar2_position': event['play_bar2_position'],
            'ball_position': event['ball_position'],
            'score_player1': event['score_player1'],
            'score_player2': event['score_player2']
        }))


########
##########
######
######
########
########
#######
##

# import json
# from channels.generic.websocket import WebsocketConsumer
# from asgiref.sync import async_to_sync

# class ChatConsumer(WebsocketConsumer):
# 	def connect(self):
# 		self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
# 		self.room_group_name = "chat_" + self.room_name
# 		async_to_sync(self.channel_layer.group_add)(
# 			self.room_group_name, self.channel_name
# 		)
# 		self.accept()

# 	def disconnect(self, close_code):
# 		async_to_sync(self.channel_layer.group_discard)(
# 			self.room_group_name, self.channel_name
# 		)

# 	def receive(self, text_data):
# 		text_data_json = json.loads(text_data)
# 		message = text_data_json["message"]

# 		async_to_sync(self.channel_layer.group_send)(
# 			self.room_group_name, {
# 				"type": "chat.message",
# 				"message": message
# 			}
# 		)
# 	def chat_message(self, event):
# 		message = event["message"]
# 		self.send(text_data=json.dumps({
# 			"message": message
# 		}))
