import { Node, Mesh, InstancedMesh, Material, metals, mesh, gelMaterial, contactMaterial } from '../engine/scene.js';
import { roundedBox, sphere, cylinder, ring, TubeGeometry, box } from '../engine/geometry.js';
import { Vec3, clamp, mix, rng, smooth, hex } from '../engine/math.js';
export class IonicVolume extends Node {
    bottom: Mesh;
    top: Mesh;
    gel: Mesh;
    positive: InstancedMesh;
    negative: InstancedMesh;
    chargesBottom: Node;
    chargesTop: Node;
    interfaceBottom: Mesh;
    interfaceTop: Mesh;
    layers: Mesh[] = [];
    seeds: Vec3[] = [];
    last = '';
    count = 80;
    constructor(public coarse = false) {
        super();
        this.bottom = mesh(this, roundedBox(5.5, .24, 3.8, .09), metals.silver, [0, 0, 0]);
        this.top = mesh(this, this.bottom.geometry, metals.silver.clone({ opacity: .5 }), [0, 2.9, 0]);
        this.top.visible = false;
        this.gel = mesh(this, roundedBox(5.2, 2.64, 3.5, .16), gelMaterial().clone({ opacity: .22, roughness: .7 }), [0, 1.45, 0]);
        const geo = sphere(.095, 18, 12);
        this.positive = this.add(new InstancedMesh(geo, new Material(0xba782a, { roughness: .57, metalness: 0 }), this.count));
        this.negative = this.add(new InstancedMesh(geo, new Material(0x2b709b, { roughness: .55, metalness: 0 }), this.count));
        this.positive.castShadow = this.negative.castShadow = false;
        const random = rng(61423);
        for (let i = 0; i < this.count * 2; i++)
            this.seeds.push([(random() - .5) * 4.65, .35 + random() * 2.12, (random() - .5) * 3.0]);
        this.chargesBottom = this.add(new Node());
        this.chargesTop = this.add(new Node());
        const minus = box(.16, .018, .035), minusMat = new Material(0x3d7ba4, { roughness: .55, emission: .10 }), plusMat = new Material(0xc79046, { roughness: .55, emission: .1 });
        const bottomMarks = this.chargesBottom.add(new InstancedMesh(minus, minusMat, 36)), topMarks = this.chargesTop.add(new InstancedMesh(minus, plusMat, 72));
        for (let z = 0; z < 4; z++)
            for (let x = 0; x < 9; x++) {
                const p: Vec3 = [-2.15 + x * .535, .134, -1.28 + z * .85], i = z * 9 + x;
                bottomMarks.set(i, p);
                topMarks.set(i * 2, [p[0], 2.766, p[2]]);
                topMarks.set(i * 2 + 1, [p[0], 2.766, p[2]], [0, Math.PI / 2, 0]);
            }
        this.interfaceBottom = mesh(this, roundedBox(5.08, .11, 3.38, .035), new Material(0xe8c68c, { roughness: .7, opacity: .3, emission: .08 }), [0, .235, 0]);
        this.interfaceTop = mesh(this, roundedBox(5.08, .11, 3.38, .035), new Material(0x9dc7dc, { roughness: .7, opacity: .3, emission: .08 }), [0, 2.66, 0]);
        this.interfaceBottom.castShadow = this.interfaceTop.castShadow = false;
        this.set(0, false, 1, 0);
    }
    set(bias: number, two: boolean, ions = 1, time = 0, topContact = 1, airGap = 0, compression = 0) {
        const key = [bias, two, ions, time, topContact, airGap, compression].join(',');
        if (key === this.last)
            return;
        this.last = key;
        const b = smooth(bias), upper = two ? clamp(topContact) : 0;
        this.top.visible = two;
        this.top.scale = [.70,1,.70];
        this.interfaceTop.scale = [.72,1,.72];
        this.chargesTop.scale = [.70,1,.70];
        const squeeze = clamp(compression) * 1.02;
        this.top.position[1] = 2.9 + airGap - squeeze;
        this.interfaceTop.position[1] = 2.66 - squeeze;
        this.chargesTop.position[1] = airGap - squeeze;
        const gelHeight = 2.64 - squeeze;
        this.gel.scale[1] = gelHeight / 2.64;
        this.gel.position[1] = .13 + gelHeight / 2;
        this.chargesBottom.visible = bias > .04;
        this.chargesTop.visible = upper > .02 && bias > .04;
        this.interfaceBottom.visible = bias > .1;
        this.interfaceTop.visible = upper > .02 && bias > .1;
        this.interfaceBottom.material.opacity = bias * .26;
        this.interfaceTop.material.opacity = bias * .30 * upper;
        this.gel.material.opacity = this.coarse ? .46 : .13;
        this.positive.visible = this.negative.visible = ions > 0;
        for (let i = 0; i < this.count; i++) {
            const initial = this.seeds[i], q = this.seeds[i + this.count];
            const layer = i < 45;
            const x = -2.12 + (i % 9) * .53, z = -1.28 + Math.floor(i / 9) * .64;
            const scaleY = (2.38 - squeeze) / 2.38;
            const compressY = (y:number)=>.28 + (y-.28)*scaleY;
            const yp = layer ? .32 + (i % 3) * .026 : compressY(.65 + (initial[1] - .35) * .85);
            const bulkN = compressY(.65 + (q[1] - .35) * .84);
            const yn = layer ? mix(bulkN, 2.54 - squeeze - (i % 3) * .026, upper) : bulkN;
            const destinationP: Vec3 = layer ? [x, yp, z] : [initial[0], yp, initial[2]], destinationN: Vec3 = layer ? [mix(q[0], x*.70, upper), yn, mix(q[2], z*.70, upper)] : [q[0], yn, q[2]];
            const p: Vec3 = [mix(initial[0], destinationP[0], b), mix(initial[1], destinationP[1], b), mix(initial[2], destinationP[2], b)];
            const n: Vec3 = [mix(q[0], destinationN[0], b), mix(q[1], destinationN[1], b), mix(q[2], destinationN[2], b)];
            // Quasi-static interpolation, not molecular dynamics. No random per-frame motion.
            const size = this.coarse ? .76 : 1;
            this.positive.set(i, p, [0, 0, 0], [size, size, size]);
            this.negative.set(i, n, [0, 0, 0], [size, size, size]);
        }
    }
    setScreening(strength:number){
        const t=clamp(strength);
        this.emphasis={top:t,bottom:t};
        const blue=hex(0x4b91ba),gold=hex(0xd29a3c);
        this.interfaceTop.material.color=blue;this.interfaceBottom.material.color=gold;
        this.interfaceTop.material.opacity=.30+.42*t;this.interfaceBottom.material.opacity=.30+.42*t;
        this.interfaceTop.material.emission=.10+.34*t;this.interfaceBottom.material.emission=.10+.34*t;
        this.gel.material.opacity=mix(.13,.055,t);
        this.top.material.opacity=.34;
        for(let i=0;i<this.count;i++){
            const interfacial=i<45,alpha=interfacial?mix(.78,1,t):mix(.64,.16,t);
            this.positive.colors.set([1,1,1,alpha],i*4);this.negative.colors.set([1,1,1,alpha],i*4);
        }
        this.positive.material.emission=.035+.11*t;this.negative.material.emission=.035+.11*t;
        this.positive.instanceVersion++;this.negative.instanceVersion++;
    }

    emphasis={top:0,bottom:0};
    emphasize(top:number,bottom:number){
        this.emphasis={top,bottom};
        const tint=(a:number,b:number,t:number)=>hex(a).map((v,k)=>mix(v,hex(b)[k],clamp(t))) as Vec3;
        this.interfaceTop.material.color=tint(0xacc6d7,0x4286b4,top);
        this.interfaceBottom.material.color=tint(0xcabda3,0xd59635,bottom);
        this.interfaceTop.material.opacity=.16+.60*top;
        this.interfaceBottom.material.opacity=.16+.60*bottom;
        this.interfaceTop.material.emission=.06+.48*top;
        this.interfaceBottom.material.emission=.06+.48*bottom;
        this.negative.material.emission=.04+.38*top;
        this.positive.material.emission=.04+.38*bottom;
        this.top.material.opacity=.28;this.gel.material.opacity=.075;
        for(let i=0;i<this.count;i++){
            const t=i<45?.30+.70*top:.24,b=i<45?.30+.70*bottom:.24;
            this.negative.colors.set([1,1,1,t],i*4);this.positive.colors.set([1,1,1,b],i*4);
        }
        this.negative.instanceVersion++;this.positive.instanceVersion++;
    }
    resetEmphasis(){
        if(this.emphasis.top===0&&this.emphasis.bottom===0)return;
        this.emphasis={top:0,bottom:0};this.last='';
        this.interfaceTop.material.color=hex(0x9dc7dc);this.interfaceBottom.material.color=hex(0xe8c68c);
        this.interfaceTop.material.emission=this.interfaceBottom.material.emission=.08;
        this.positive.material.emission=this.negative.material.emission=0;this.top.material.opacity=.5;
        for(let i=0;i<this.count;i++){this.positive.colors.set([1,1,1,1],i*4);this.negative.colors.set([1,1,1,1],i*4);}
        this.positive.instanceVersion++;this.negative.instanceVersion++;
    }

}
