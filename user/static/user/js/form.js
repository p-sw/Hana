page = {
    init: function () {
        this.initEvent();
    },

    initEvent: function () {
        if (document.querySelector("input[type='submit']")) {
            document.querySelector("input[type='submit']").disabled = true;
        }

        Array.prototype.forEach.call(document.querySelectorAll('.form-control'), function (el) {
            el.addEventListener('input', function (e) {
                if (e.target.classList.contains('error')) {
                    e.target.classList.remove('error');
                    if (e.target.parentNode.querySelector('.alert-danger')) {
                        e.target.parentNode.removeChild(e.target.parentNode.querySelector('.alert-danger'));
                    }
                }
                if (document.querySelectorAll('.error').length === 0) {
                    document.querySelector('input[type="submit"]').disabled = false;
                }
            });
        });

        if (document.querySelector('#password_check')) {
            document.querySelector('#password_check').addEventListener('input', function () {
                if (this.value !== document.querySelector('#password').value && !('error' in this.classList)) {
                    this.classList.add('error');
                } else if (this.value === document.querySelector('#password')) {
                    this.classList.remove('error');
                }
            });
        }

        if (document.querySelector('input[type="email"]')) {
            document.querySelector('input[type="email"]').addEventListener('input', function () {
                if (!this.value.match(/^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/)) {
                    this.classList.add('error');
                } else {
                    this.classList.remove('error');
                }
            });
        }

        if (document.querySelector('input[type="submit"]')) {
            document.querySelector('input[type="submit"]').addEventListener('click', function (e) {
                e.preventDefault();
                if (document.querySelectorAll('.error').length === 0) {
                    document.querySelector('form').submit();
                }

                e.target.disabled = true;
                e.target.value = "로딩 중...";
            });
        }
    }
}