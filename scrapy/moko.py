import pymongo as pm

if __name__ == '__main__':
    # 获取连接
    client = pm.MongoClient('123.207.27.181', 27011)

    # 连接目标数据库
    db = client.moko

    # 数据库用户验证
    # db.authenticate("dba", "dba")

    post = {
        "id": "111112",
        "level": "MVP",
        "real": 1,
        "profile": '111',
        'thumb': '2222',
        'nikename': '222',
        'age': '1',
        'follows': 20
    }

    db.col.insert_one(post)

    print(db.col.find_one())

