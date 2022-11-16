class StarManager {
    constructor() {
        // get current favorite status
        fetch('/api/favorite/get-favorite-by-id', {
            method: 'GET',
        }).then((response) => response.json()).then((data) => {
            this.isFavorite = data["exists"];

            this.star = document.querySelector("#star img");
            this.star_normal = this.star.src;
            this.star_active = this.star.dataset.src;

            this.updateStar();
        })
    }

    updateStar() {
        if (this.isFavorite) {
            this.star.src = this.star_active;
        } else {
            this.star.src = this.star_normal;
        }
    }

    toggleStar() {
        // toggle using server api

        this.isFavorite = !this.isFavorite;
        this.updateStar();
    }
}

class Nav {
    constructor (galleryid) {
        this.nav = document.querySelector('nav');
        this.galleryid = galleryid;

        this.getScript().then((data) => {
            this.nav.querySelector("h1").innerText = /"title":"([^"]+)"/.exec(data)[1];
        });

        this.nav.querySelector("#menu-open").addEventListener("click", this.openMenu.bind(this));
        this.nav.querySelector("#menu-close").addEventListener("click", this.closeMenu.bind(this));
        this.nav.querySelector('#back').addEventListener("click", () => {
            window.history.back();
        })
        this.nav.querySelector("#home").addEventListener("click", () => {
            window.location.href = "/";
        })

        this.starManager = new StarManager();
        this.nav.querySelector("#star").addEventListener("click", this.starManager.toggleStar.bind(this.starManager));
    }

    getScript () {
        return fetch(`/api/get-js?url=https://ltn.hitomi.la/galleries/${this.galleryid}.js`, {
            method: 'GET',
            cache: 'force-cache',
        }).then(response => response.text())
    }

    openMenu() {
        this.nav.querySelector("#menu-open").style.display = "none";
        this.nav.querySelector("#menu-close").style.display = "block";
        this.nav.querySelector("#main-menu").classList.remove("closed");
        this.nav.querySelector("#main-menu").classList.add("opened");
    }

    closeMenu() {
        this.nav.querySelector("#menu-open").style.display = "block";
        this.nav.querySelector("#menu-close").style.display = "none";
        this.nav.querySelector("#main-menu").classList.add("closed");
        this.nav.querySelector("#main-menu").classList.remove("opened");
    }
}