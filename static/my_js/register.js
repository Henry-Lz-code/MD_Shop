let vm = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_image_code: false,
        error_sms_code: false,
        error_allow: false,
        error_name_message:"请输入5-20个字符的用户名",
        error_password_message:"请求输入8-20位的密码",
        error_password2_message:"两次输入的密码不一样",
        error_phone_message:"手机号格式错误",
        error_image_code_message:"请填写图片验证码",
        error_sms_code_message:"请填写短信验证码",
        error_allow_message:"请勾选用户协议",
        image_code_id: "",
        image_code_url: "",
        sms_code_tip: "获取短信验证码",
        sending_flag: false,
        username: "",
        password: "",
        password2: "",
        mobile: "",
        image_code: "",
        sms_code: "",
        allow: true
    },
    mounted: function () {
        //向服务器获取图片验证码
        this.generate_image_code();
    },
    methods: {
        generateUUID: function () {
            let d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                let r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
        generate_image_code: function () {
            // 生成一个编号 : 严格一点的使用uuid保证编号唯一， 不是很严谨的情况下，也可以使用时间戳
            this.image_code_id = this.generateUUID();
            // 设置页面中图片验证码img标签的src属性
            this.image_code_url = this.host + "/image_codes/" + this.image_code_id + "/";
            console.log(this.image_code_url);
        },
        check_username: function () {
            //检查用户名格式
            let re = /^[a-zA-Z0-9_-]{5,20}$/;
            if(re.test(this.username)){
                this.error_name = false;
            }else{
                this.error_name_message = "请输入5-20个字符的用户名";
                this.error_name = true;
            }
            //检查用户名是否重名
            if(this.error_name===false){
                let url = this.host + '/usernames/' + this.username + '/count/';
                axios.get(url, {responseType: 'json'}).then(response =>{
                    if(response.data.count > 0){
                        this.error_name_message = "用户名已存在";
                        this.error_name = true;
                    }else{
                        this.error_name = false;
                    }
                }).catch(error =>{
                    console.log(error.response);
                })
            }

        },
        check_pwd: function () {
            //检查密码的格式
            let re = /^[0-9a-zA-Z.*]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false;
            }else{
                this.error_password_message = "密码只能有5-20个字母数字或.*组成";
                this.error_password = true;
            }
        },
        check_pwd2: function(){
            //检查两次输入的密码是否一致
            if(this.password !== this.password2){
                this.error_check_password = true;
            }else{
                this.error_check_password = false;
            }
        },
        check_phone: function () {
            //检查手机号的格式
            let re = /^1[345789]\d{9}$/;
            if(re.test(this.mobile)){
                this.error_phone = false;
            }else{
                this.error_phone_message = "手机号格式错误";
                this.error_phone = true;
            }
            if(this.error_phone===false){
                let url = this.host + '/mobiles/' + this.mobile + '/count/';
                axios.get(url, {responseType: "json"}).then(response =>{
                    if(response.data.count > 0){
                        this.error_phone_message = "手机号已存在";
                        this.error_phone = true;
                    }else{
                        this.error_phone = false;
                    }
                }).catch(error =>{
                    console.log(error.response);
                })
            }
        },
        check_image_code: function () {
            //检查图片验证码是否填写
            if(!this.image_code){
                this.error_image_code_message = "请输入短信验证码";
                this.error_image_code = true;
            }else{
                this.error_image_code = false;
            }
        },
        check_sms_code: function () {
            //检查短信验证码
            if(!this.sms_code){
                this.error_sms_code_message = "请填写短信验证码";
                this.error_sms_code = true;
            }else{
                this.error_sms_code = false;
            }
        },
        check_allow: function () {
            //检查是否勾选了同意协议
            this.allow? this.error_allow = false: this.error_allow = true
        },
        send_sms_code: function () {
            //发送短信验证码
            if(this.sending_flag === true){
                return;
            }
            //将发送验证码的标志位置为
            this.sending_flag = true;
            //校验参数,保证有数据输入
            this.check_phone();
            this.check_image_code();

            //根据校验后参数判断是否能够发送验证码
            if(this.error_phone === true || this.error_image_code === true){
                this.sending_flag = false;
                return;
            }
            let url = this.host + '/sms_codes/' + this.mobile + '/?image_code=' + this.image_code + '&image_code_id=' + this.image_code_id;
            axios.get(url, {responseType: 'json'}).then(response =>{
                if(response.data.code == '0'){
                    let num = 60;
                    let t = setInterval(()=>{
                        if(num === 1){
                            clearInterval(t);
                            this.sms_code_tip = "获取短信验证码";
                            this.sending_flag = false;
                        }else{
                            num -= 1;
                            this.sms_code_tip = num + "秒";
                }
                    }, 1000, 60)
                }else{
                    if(response.data.code == "4001"){
                        this.error_image_code_message = response.data.errmsg;
                        this.error_image_code = true;
                    }
                    else{
                        this.error_sms_code_message = response.data.errmsg;
                        this.error_sms_code = true;
                    }
                    this.generate_image_code();
                    this.sending_flag = false;
            }
            }).catch(error =>{
                console.log(error.response);
                this.sending_flag = false;
            })
        },
        on_submit(){
            this.check_username();
            this.check_pwd();
            this.check_pwd2();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();

            if(this.error_name === true || this.error_password === true || this.error_check_password === true
            || this.error_phone === true || this.error_sms_code === true || this.error_allow === true){
                window.event.returnValue = false;
            }
        }
    }
});


























