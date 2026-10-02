import { Frame, LabelSpec } from '../worlds/WorldManager.js';
import { transform, clamp } from '../engine/math.js';
export class Labels {
    root: HTMLDivElement;
    svg: SVGSVGElement;
    elements: HTMLDivElement[] = [];
    last = '';
    overlaps = 0;
    outOfBounds = 0;
    constructor(parent: HTMLElement) { this.root = document.createElement('div'); this.root.className = 'label-layer'; parent.append(this.root); this.svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg'); this.svg.classList.add('leader'); this.root.append(this.svg); }
    update(frame: Frame, blocked: DOMRect[], hidden = false) {
        this.root.classList.toggle('hidden', hidden);
        if (hidden)
            return;
        const camera = frame.other && frame.other.blend > .5 ? frame.other.camera : frame.camera;
        const w = innerWidth, h = innerHeight;
        const zone=document.querySelector<HTMLElement>("#model-zone")!.getBoundingClientRect();
        const desc = frame.labels.slice(0, 5), key = desc.map(x => x.title + '|' + x.detail).join('/');
        if (key !== this.last) {
            this.last = key;
            this.elements.forEach(e => e.remove());
            this.elements = desc.map(l => { const d = document.createElement('div'); d.className = 'world-label'; const span = document.createElement('span'); span.textContent = l.title; d.append(span); if (l.detail) {
                const small = document.createElement('small');
                small.textContent = l.detail;
                d.append(small);
            } this.root.append(d); return d; });
        }
        this.svg.innerHTML = '';
        this.svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
        const placed: DOMRect[] = [];
        this.overlaps = 0;
        this.outOfBounds = 0;
        const overlap = (a: {
            x: number;
            y: number;
            width: number;
            height: number;
        }, b: DOMRect) => Math.max(0, Math.min(a.x + a.width, b.right) - Math.max(a.x, b.left)) * Math.max(0, Math.min(a.y + a.height, b.bottom) - Math.max(a.y, b.top));
        desc.forEach((l, i) => {
            const p = l.node ? transform(l.node.world, l.point) : l.point;
            const screen = camera.project(p, w, h), el = this.elements[i];
            el.style.visibility = screen.valid ? 'visible' : 'hidden';
            if (!screen.valid)
                return;
            const strength=l.emphasis;
            if(strength!==undefined){const q=clamp(strength);el.style.opacity=String(.65+.35*q);el.style.borderColor=l.tone==='gold'?`rgba(177,126,40,${.25+.65*q})`:`rgba(54,111,146,${.25+.65*q})`;el.style.backgroundColor=l.tone==='gold'?`rgba(249,238,213,${.68+.29*q})`:`rgba(227,241,249,${.68+.29*q})`;el.style.color=l.tone==='gold'?'#845b23':'#245e83';}
            else{el.style.opacity='';el.style.borderColor='';el.style.backgroundColor='';el.style.color='';}
            const ew = el.offsetWidth, eh = el.offsetHeight;
            const ox = (l.offset?.[0] || 90) * w / 1920, oy = (l.offset?.[1] || 30) * h / 1080;
            const anchor = { x: screen.x, y: screen.y };
            const candidates = [[ox, oy], [ox, oy + 70], [-ox - ew, oy], [ox, -oy - eh], [ox, oy - 110], [-ox - ew, -oy - eh], [ox * 1.5, oy + 110], [-ox - ew, oy + 140], [zone.left+6-anchor.x,0], [zone.right-ew-6-anchor.x,0]];
            let best = { x: 0, y: 0, score: Infinity };
            for (const [dx, dy] of candidates) {
                const x = clamp(anchor.x + dx, zone.left+4, zone.right-4-ew), y = clamp(anchor.y + dy, zone.top+4, zone.bottom-4-eh), rect = { x, y, width: ew, height: eh };
                let score = Math.hypot(x - (anchor.x + ox), y - (anchor.y + oy)) * .6;
                for (const b of [...blocked, ...placed])
                    score += overlap(rect, b) * 20;
                if (score < best.score)
                    best = { x, y, score };
            }
            el.style.left = best.x + 'px';
            el.style.top = best.y + 'px';
            const rect = el.getBoundingClientRect();
            for (const b of [...blocked, ...placed])
                if (overlap(rect, b) > 4)
                    this.overlaps++;
            placed.push(rect);
            if (rect.left < 0 || rect.top < 0 || rect.right > w || rect.bottom > h)
                this.outOfBounds++;
            const endX = anchor.x < rect.left ? rect.left : anchor.x > rect.right ? rect.right : clamp(anchor.x, rect.left + 8, rect.right - 8), endY = clamp(anchor.y, rect.top + 5, rect.bottom - 5);
            if (anchor.x > 0 && anchor.x < w && anchor.y > h * .20 && anchor.y < h * .94) {
                const line = document.createElementNS(this.svg.namespaceURI, 'line');
                line.setAttribute('x1', anchor.x.toFixed(1));
                line.setAttribute('y1', anchor.y.toFixed(1));
                line.setAttribute('x2', endX.toFixed(1));
                line.setAttribute('y2', endY.toFixed(1));
                this.svg.append(line);
                const dot = document.createElementNS(this.svg.namespaceURI, 'circle');
                dot.setAttribute('cx', anchor.x.toFixed(1));
                dot.setAttribute('cy', anchor.y.toFixed(1));
                dot.setAttribute('r', '2.2');
                this.svg.append(dot);
            }
        });
    }
}
