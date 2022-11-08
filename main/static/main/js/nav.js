class Nav {
    constructor() {
        this.toolbar = document.querySelector('.toolbar');

        this.nav = this.toolbar.querySelector('nav');
        this.navOpener = this.nav.querySelector('div.control button.nav-opener');
        this.navCloser = this.nav.querySelector('div.control button.nav-closer');

        this.contents = this.nav.querySelectorAll('div.content button');

        this.navOpener.addEventListener('click', this.open.bind(this));
        this.navCloser.addEventListener('click', this.close.bind(this));
    }

    open() {
        this.navOpener.classList.add("disabled");
        this.navCloser.classList.remove("disabled");
        this.contents.forEach((item) => {
            item.classList.add('visible');
        });
    }

    close() {
        this.navOpener.classList.remove("disabled");
        this.navCloser.classList.add("disabled");
        this.contents.forEach((item) => {
            item.classList.remove('visible');
        })
    }
}