import sqlite3 as db
import os
import glob

def find_tippo_db(base_dir: str) -> str | None:
    # 1) 일반적인 패턴: kit_user_*#
    candidates = glob.glob(os.path.join(base_dir, "kit_user_*#"))
    # 2) 혹시 '#' 없이 저장된 경우까지 커버
    if not candidates:
        candidates = glob.glob(os.path.join(base_dir, "kit_user_*"))

    if not candidates:
        return None

    # 최신 수정순으로 가장 가능성 높은 것 선택
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]

def parse_contact(db_path = r'D:\Evidences\Android\in\Tippo\com.flipped.gobump\databases\kit_user_My0zYzU4YTllZi0xNGQ5LTRiMzQtYThiOS1kYTU5MmQ3ODhlNzI=#'):
    conn = db.connect(db_path)
    cursor  = conn.cursor()

    cursor.execute('select * from user')
    rows = cursor.fetchall()

    resultItems = []
    for row in rows:
        # print(row)
        rec = {
            'uid' : row[0],
            'name' : row[1],
            'profile_url' : row[3]
        }

        # 중복 체크 후 append
        if not any(d['uid'] == rec['uid'] for d in resultItems):
            resultItems.append(rec)
    # print(resultItems)

    conn.close()
    conn.close()
    return resultItems

def set_table_value(contacts):
    result_db_path = r'D:\Evidences\Android\out\Tippo\Tippo.db'

    # 1) 상위 폴더 자동 생성 (이미 있으면 무시)
    os.makedirs(os.path.dirname(result_db_path), exist_ok=True)

    dst_conn = db.connect(result_db_path)
    dst_cur  = dst_conn.cursor()
    dst_cur.execute("""
    CREATE TABLE IF NOT EXISTS T_Contact_Tippo (
        UID TEXT PRIMARY KEY,
        Name TEXT,
        ProfilePic TEXT
    )
    """)

    dst_cur.executemany("""
    INSERT INTO T_Contact_Tippo (UID, Name, ProfilePic)
    VALUES (:uid, :name, :profile_url)
    ON CONFLICT(UID) DO UPDATE SET
        Name = excluded.Name,
        ProfilePic = excluded.ProfilePic;
    """, contacts)

    dst_conn.commit()
    dst_cur.close()
    dst_conn.close()

    print(f"[+] {len(contacts)} record(s) saved to {result_db_path} -> T_Contact_Tippo")


if __name__ == "__main__":
    evidences_dir = r'D:\Evidences\Android\in\Tippo\com.flipped.gobump\databases'
    db_path = find_tippo_db(evidences_dir)
    contacts = parse_contact(db_path)
    set_table_value(contacts)
    print()



