class GalleryBlock {
    constructor() {
        this.galleries_per_page = 25;
        this.query = decodeURIComponent(window.location.href.replace(/.*sserve\.work\//, ''));
        if (/^\?page=\d+$/.test(this.query)) {
            this.query = parseInt(this.query.replace(/^\?page=/, ''), 10);
        } else {
            this.query = 1;
        }

        this.start_byte = (this.query - 1) * this.galleries_per_page * 4;
        this.end_byte = this.start_byte + this.galleries_per_page * 4 - 1;
    }

    load() {
        return fetch(`/api/get-nozomi?start=${this.start_byte}&end=${this.end_byte}`, {
            method: 'GET',
        }).then(response => {
            // this.total_items = parseInt(response.headers.get("Content-Range").replace(/^[Bb]ytes \d+-\d+\//, '')) / 4;
            return response.arrayBuffer();
        }).then((buffer) => {
            return new DataView(buffer);
        }).then((data) => {
            const total = data.byteLength / 4;
            let nozomi = [];
            for (let i=0;i<total;i++) {
                nozomi.push(data.getUint32(i*4, false));
            }
            return nozomi;
        })
    }

    put(f) {
        f.then((nozomi) => {
            for (let item of nozomi) {
                fetch(`/api/get-galleryblock?id=${item}`, {
                    method: 'GET',
                }).then(response => {
                    return response.text();
                }).then(html => {
                    let block = document.createElement("article");
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
                    }
                    if (img) {
                        img.src = "/api/get-image?url=https:"+img.dataset.src;
                        img.classList.add("lazyload");
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