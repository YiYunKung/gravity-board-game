# ♟️重力四子棋｜Gravity Board Game
* 可點擊觀看 [遊戲遊玩及程式介紹影片](https://youtu.be/w9rfuLpxZEw) <br>
* 前往下載詳細說明－ [重力四子棋報告](https://github.com/YiYunKung/Gravity4pieceChessGame/blob/main/%E9%87%8D%E5%8A%9B%E5%9B%9B%E5%AD%90%E6%A3%8B%E5%A0%B1%E5%91%8A.docx)

## 遊戲規則
兩client端接連入後，即開始遊戲，其中一方為紅棋，一方為黃棋。<br>
雙方輪流且每人一回合有一次下棋機會，以先連入的client端優先下棋。<br>
下棋時，點擊其中一行，棋子會落於該行**當前的最底層**。<br>
當有任一顏色的四個棋子連成一線（包含斜線），顯示遊戲結果，雙方client斷線並停止介面更新。<br>

![image](https://github.com/user-attachments/assets/e7a6fb14-3f48-40d2-8978-d7b52fc0c37c)

## 程式功能
* 接收滑鼠點擊位置
* 判斷該行的最底可下棋位置
* 傳遞落棋座標及顏色 (ex: client1->server, server->client2)
* 接收座標、顏色並更新於GUI介面
* 雙方輪流取得操作權
* 判斷遊戲勝負結果
* 結束遊戲後停止GUI介面更新（取消綁定滑鼠事件）
