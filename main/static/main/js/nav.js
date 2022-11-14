class Nav {
    constructor() {
        this.toolbar = document.querySelector('.toolbar');

        this.nav = this.toolbar.querySelector('nav');
        this.navOpener = this.nav.querySelector('div.control button.nav-opener');
        this.navCloser = this.nav.querySelector('div.control button.nav-closer');

        this.contents = this.nav.querySelectorAll('div.content button');

        this.navOpener.addEventListener('click', this.open.bind(this));
        this.navCloser.addEventListener('click', this.close.bind(this));

        this.queryArea = new QueryArea();
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

class QueryArea {
    constructor() {
        this.toolbar = document.querySelector('.toolbar');
        this.suggestor = this.toolbar.querySelector('div.searchbar-container div.suggests');

        this.toolbar.querySelector("div.searchbar-container").addEventListener("click", e => {
            document.querySelector(".toolbar div.searchbar-input input").focus();
        })

        this.tag_container = this.toolbar.querySelector('div.searchbar-input div.tags');
        this.queryArea = this.toolbar.querySelector("input");
        this.queryArea.addEventListener('input', this.input.bind(this));
    }

    input() {
        this.suggestor.innerHTML = '';
        let query = /(?:[^:]+:)?([a-zA-Z_\s]*)/.exec(this.queryArea.value)[1];
        if (query.length > 0) {
            fetch(`/api/get-recommendation-tag?tag=${query}`, {
                method: 'GET',
            }).then((response) => response.json()).then((data) => {
                for (let tag of data.tags) {
                    let item = document.createElement("div");
                    item.classList.add("item");
                    item.innerHTML = `<span>${tag}</span>`;
                    item.onclick = (e) => {
                        let ti = document.createElement("div");
                        ti.classList.add("item");
                        ti.innerText = e.target.innerText;

                        let close = document.createElement("button");
                        close.innerText = "x";
                        close.onclick = (e) => {
                            e.target.parentElement.remove();
                        }

                        ti.appendChild(close);

                        this.queryArea.value = "";
                        this.tag_container.appendChild(ti);
                        this.suggestor.innerHTML = '';
                    }
                    this.suggestor.appendChild(item);
                }
            })
        }

    }
}