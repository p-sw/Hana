function loadErrorHandler(e) {
    setTimeout(() => {
        if (/&t=/.test(e.target.src)) {
            e.target.src = e.target.src.replace(/&t=\d+/, `&t=${Date.now()}`);
        } else {
            e.target.src = e.target.src + "&t=" + Date.now();
        }
    }, 1500);
}

class PageNavigator {
    constructor(pages) {
        this.max_page = pages

        this.query = decodeURIComponent(window.location.search);
        if (/[?&]page=\d+/.test(this.query)) {
            this.current_page = parseInt(/[?&]page=(\d+)/.exec(this.query)[1], 10);
        } else {
            this.current_page = 1;
        }

        /* configurations */
        this.build_parent = document.querySelector("section#page-navigation")

        this.page_button_per_page = 10;
    }

    build() {
        let page_navigator = document.createElement("nav");
        page_navigator.classList.add("page-navigator");

        let page_min = Math.floor(this.current_page / 10) * 10 + 1;
        let page_max = Math.min(page_min + (this.page_button_per_page - 1), this.max_page);

        let page_prev = document.createElement("a");
        page_prev.classList.add("page-prev");
        page_prev.href = this.build_query(this.current_page - 1);
        page_navigator.appendChild(page_prev);

        for (let i=page_min;i<=page_max;i++) {
            let page_button = document.createElement("a");
            page_button.classList.add("page-button");
            page_button.href = this.build_query(i);
            page_button.innerText = i.toString();
            if (i === this.current_page) {
                page_button.classList.add("current-page");
                page_button.href = '';
            }
            page_navigator.appendChild(page_button);
        }

        let page_next = document.createElement("a");
        page_next.classList.add("page-next");
        page_next.href = this.build_query(this.current_page + 1);
        page_navigator.appendChild(page_next);

        this.build_parent.appendChild(page_navigator);
    }

    build_query(page) {
        if (/[?&]page=\d+/.test(this.query)) {
            return this.query.replace(/page=\d+/, `page=${page}`);
        } else if (this.query.length){
            return `${this.query}&page=${page}`;
        } else {
            return `?page=${page}`;
        }
    }
}

class GalleryBlock {
    constructor() {
        this.galleries_per_page = 25;
        this.query = decodeURIComponent(window.location.href.replace(/.*sserve\.work\//, ''));
        if (/^\?page=\d+$/.test(this.query)) {
            this.page = parseInt(this.query.replace(/^\?page=/, ''), 10);
        } else {
            this.page = 1;
        }
    }

    load() {
        return fetch(`/api/get-nozomi`, {
            method: 'GET',
        }).then(response => {
            // this.total_items = parseInt(response.headers.get("Content-Range").replace(/^[Bb]ytes \d+-\d+\//, '')) / 4;
            return response.arrayBuffer();
        }).then((buffer) => {
            return new DataView(buffer);
        }).then((data) => {
            const total_galleries = data.byteLength / 4;
            // init page navigator
            let page_navigator = new PageNavigator(Math.ceil(total_galleries / this.galleries_per_page));
            page_navigator.build();

            let nozomi = [];
            for (let i=(this.page - 1) * this.galleries_per_page;i<Math.min(total_galleries, this.galleries_per_page * this.page);i++) {
                nozomi.push(data.getUint32(i*4, false));
            }
            return nozomi;
        })
    }

    put(f) {
        f.then((nozomi) => {
            document.querySelector("#loading-content").remove();
            for (let item of nozomi) {
                fetch(`/api/get-galleryblock?id=${item}`, {
                    method: 'GET',
                }).then(response => {
                    return response.text();
                }).then(html => {
                    let block = document.createElement("article");
                    block.setAttribute("style", `order: ${nozomi.indexOf(item)};`);
                    block.classList.add("gallery-block");
                    block.innerHTML = html;
                    return block;
                }).then(block => { // post-processing
                    // remove 2nd, 3rd image
                    block.querySelector("div a.lillie div[class*=-img-cont] div[class*=-img2]").remove()
                    block.querySelector("div a.lillie div[class*=-img-cont] div[class*=-img-back]").remove()
                    // set thumbnail
                    let src = block.querySelector("div a.lillie div[class*=-img-cont] picture source");
                    let img = block.querySelector("div a.lillie div[class*=-img-cont] picture img");
                    if (src) {
                        src.src = "/api/get-image?url=https:"+/(\S+)\s1x/.exec(src.dataset.srcset)[1];
                        src.classList.add("lazyload");
                        src.addEventListener("error", loadErrorHandler);
                    }
                    if (img) {
                        img.src = "/api/get-image?url=https:"+img.dataset.src;
                        img.classList.add("lazyload");
                        img.addEventListener("error", loadErrorHandler);
                    }
                    // add column container, add all thing except image container
                    let col = document.createElement("div");
                    col.classList.add("col");
                    col.appendChild(block.querySelector("div h1.lillie"));
                    col.appendChild(block.querySelector("div div.artist-list"))
                    col.appendChild(block.querySelector("div div[class*=-content]"))
                    block.querySelector("div").appendChild(col);
                    block.setAttribute("style", `order: ${nozomi.indexOf(item)};`);
                    document.getElementById("gallery").appendChild(block);
                })
            }
        })
    }
}

gallery = new GalleryBlock();
gallery.put(gallery.load());