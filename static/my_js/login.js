let vm = new Vue({
    el: "#app",
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        username: "",
        password: "",
        error_username: false,
        error_username_message: "",
        error_password: false,
        error_password_message: "",
        remembered: false
    },
    methods: {
        check_username: function () {
            let re = /^[0-9a-zA-Z_-]{5,20}$/;
            if(re.test(this.username)) {
                this.error_username = false;
            }else{
                this.error_username = true;
                this.error_username_message = "用户名不存在"
            }
            if(this.error_username === false){
                let url = this.host + '/usernames/' + this.username + '/count/';
                axios.get(url, {responseType: 'json'}).then((response)=>{
                    if(response.data.count > 0){
                        this.error_username = false;
                    }else{
                        this.error_username = true;
                        this.error_username_message = "用户名不存在";
                    }
                }).catch(error=>{
                    console.log(error.response);
                })
            }
        },
        check_pwd: function () {
            let re = /^[0-9a-zA-Z.*]{8,20}$/;
            if(re.test(this.password)){
                this.error_password = false;
            }else{
                this.error_password = true;
                this.error_password_message = "密码错误";
            }
        },
        on_submit(){
            this.check_username();
            this.check_pwd();
            if((this.error_username === true)||(this.error_password === true)){
                window.event.returnValue = false
            }
        }
    }
});