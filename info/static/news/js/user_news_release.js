$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault()

        $('#rich_content').val(tinyMCE.get('rich_content').getContent());
        // 发布完毕之后需要选中我的发布新闻
        $(this).ajaxSubmit({
            url: "/user/news_release",
            type: "POST",
            success: function (resp) {
                if (resp.errno == "0") {
                    // 选中索引为6的左边单菜单
                    window.parent.fnChangeMenu(6)
                    // 滚动到顶部
                    window.parent.scrollTo(0, 0)
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})