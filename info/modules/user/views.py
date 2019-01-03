from flask import render_template, g, request, jsonify
from info.modules.user import user_blu
from info.utils.response_code import error_map, RET


@user_blu.route("/user_info")
def user_info():
    return render_template("news/user.html", user=g.user.to_dict())


@user_blu.route("/base_info", methods=['GET', 'POST'])
def base_info():
    user =g.user
    if request.method =='GET':
        return render_template("news/user_base_info.html", user=user.to_dict())

    # POST 提交资料
    # 获取参数
    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")
    # 校验参数
    if not all([signature, nick_name, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    if gender not in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.PARAMERR, errmsg=error_map[RET.PARAMERR])

    # 修改用户数据
    user.nick_name = nick_name
    user.signature = signature
    user.gender = gender

    #json返回
    return jsonify(errno=RET.OK,errmsg=error_map[RET.OK])
