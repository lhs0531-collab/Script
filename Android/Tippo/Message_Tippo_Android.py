import sqlite3 as db
import os
import json 

OUT_DB = r"D:\Evidences\Android\out\Tippo\Tippo.db"

def find_tippo_db(base_dir: str) -> str | None:
    target_file_name = r'storage'

    for root, dirs, files in os.walk(base_dir):
        # 현재 디렉토리에서 찾고자 하는 하위 경로가 있는지 확인
        db_full_path = os.path.join(root, target_file_name)

        # 경로가 존재하는지 확인
        if os.path.exists(db_full_path):
            return db_full_path
    return None

def get_name(uid : str):
    # Tippo.db 연결 → T_Contact_Tippo 테이블 조회
    with db.connect(OUT_DB) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT Name FROM T_Contact_Tippo WHERE UID = ?",
            (uid,)
        )
        row = cur.fetchone()
    if row:
        name = row[0]
        # print("[+] Found name:", name)
        conn.close()
        return name
    return None

def get_action_type(my_uid, sender_id):
    if sender_id == my_uid:
        return 'Outgoing'
    else:
        return 'Incoming'

def parse_messages(db_path = r'D:\\Evidences\\Android\\in\\Tippo\\com.flipped.gobump\\files\\qd46yzrfqaw5f\\3-3c58a9ef-14d9-4b34-a8b9-da592d788e72\\storage'):
    my_uid = os.path.basename(os.path.dirname(db_path))
    my_name = get_name(my_uid)

    conn = db.connect(db_path)
    cursor  = conn.cursor()

    cursor.execute('select * from RCT_MESSAGE')
    rows = cursor.fetchall()

    resultItems = []
    for row in rows:
        # print(row)
        content_json = json.loads(row[8])
        sender_id = row[10]
        chatroom_id = row[1]
        chat_room_title = get_name(chatroom_id)
        message = content_json['content']
 
        rec = {
            'msg_idx' : row[0],
            'actiontype' : get_action_type(my_uid, sender_id),
            'chatroom_id' : chatroom_id,
            'chatroom_title' : chat_room_title,
            'chat_member' : f"{chat_room_title}, {my_name}", 
            'sender_id' : sender_id,
            'sender' : get_name(sender_id),
            'content' : message
        }

        # 중복 체크 후 append
        if not any(d['msg_idx'] == rec['msg_idx'] for d in resultItems):
            resultItems.append(rec)
    # print(resultItems)

    conn.close()
    return resultItems

def set_table_value(contacts):
    result_db_path = OUT_DB

    # 1) 상위 폴더 자동 생성 (이미 있으면 무시)
    os.makedirs(os.path.dirname(result_db_path), exist_ok=True)

    dst_conn = db.connect(result_db_path)
    dst_cur  = dst_conn.cursor()
    dst_cur.execute("""
    CREATE TABLE IF NOT EXISTS T_Message_Tippo (
        idx INTEGER PRIMARY KEY,
        ActionType TEXT,
        ChatRoomTitle TEXT,            
        ChatMember TEXT,
        Sender TEXT,
        Message TEXT,
        ChatRoomId TEXT,
        SenderId TEXT
    )
    """)

    dst_cur.executemany("""
    INSERT INTO T_Message_Tippo (idx, ActionType, ChatRoomTitle, ChatMember, Sender, Message, ChatRoomId, SenderId)
    VALUES (:msg_idx, :actiontype, :chatroom_title, :chat_member, :sender, :content, :chatroom_id, :sender_id)
    ON CONFLICT(idx) DO UPDATE SET
        ActionType = excluded.ActionType,
        ChatRoomTitle = excluded.ChatRoomTitle,            
        ChatMember = excluded.ChatMember,
        Sender = excluded.Sender,
        Message = excluded.Message,
        ChatRoomId = excluded.ChatRoomId,
        SenderId = excluded.SenderId
    """, contacts)

    dst_conn.commit()
    dst_cur.close()
    dst_conn.close()

    print(f"[+] {len(contacts)} record(s) saved to {result_db_path} -> T_Message_Tippo")


if __name__ == "__main__":
    evidences_dir = r'D:\Evidences\Android\in\Tippo\com.flipped.gobump\files'
    db_path = find_tippo_db(evidences_dir)
    contacts = parse_messages(db_path)
    set_table_value(contacts)