import { Mat4, identity, lookAt, ortho, multiply, Vec3, transform } from './math.js';
import { Geometry } from './geometry.js';
import { Node, Mesh, InstancedMesh } from './scene.js';
import { CameraRig } from './camera.js';
const vertex = `#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;
layout(location=1) in vec3 aNormal;
layout(location=2) in vec2 aUv;
layout(location=3) in mat4 aInstance;
layout(location=7) in vec4 aColor;
layout(location=8) in mat3 aInstanceNormal;
uniform mat4 uModel,uVP,uLight;uniform mat3 uNormal;
uniform bool uInstanced;
out vec3 vPosition,vNormal;out vec2 vUv;out vec4 vShadow,vColor;
void main(){mat4 m=uModel;if(uInstanced)m=m*aInstance;vec4 p=m*vec4(aPosition,1.0);vPosition=p.xyz;vNormal=normalize(uNormal*(uInstanced?aInstanceNormal*aNormal:aNormal));vUv=aUv;vShadow=uLight*p;vColor=uInstanced?aColor:vec4(1.0);gl_Position=uVP*p;}`;
const fragment = `#version 300 es
precision highp float;
in vec3 vPosition,vNormal;in vec2 vUv;in vec4 vShadow,vColor;
out vec4 frag;
uniform vec3 uColor,uEye; uniform vec2 uViewport;
uniform float uMetal,uRough,uOpacity,uEmission,uSoft,uPattern;
uniform bool uShadowOn,uReceive;
uniform sampler2D uShadow;
const float PI=3.14159265359;
vec3 backdrop(vec2 p){vec2 d=(p-vec2(.57,.62))*vec2(.90,1.0);float fall=clamp(length(d)*1.05,0.,1.);return mix(vec3(.979,.985,.990),vec3(.878,.918,.946),fall);}

float distribution(float nh,float r){float a=r*r,a2=a*a,d=nh*nh*(a2-1.0)+1.0;return a2/(PI*d*d+.0001);}
float smith(float nv,float r){float k=(r+1.0)*(r+1.0)*.125;return nv/(nv*(1.0-k)+k);}
vec3 fresnel(float hv,vec3 f0){return f0+(1.0-f0)*pow(1.0-hv,5.0);}
vec3 lamp(vec3 n,vec3 v,vec3 l,vec3 c,vec3 base,vec3 f0,float rough){vec3 h=normalize(v+l);float nl=max(dot(n,l),0.0),nv=max(dot(n,v),.005),nh=max(dot(n,h),0.0),hv=max(dot(h,v),0.0);vec3 f=fresnel(hv,f0);vec3 spec=distribution(nh,rough)*smith(nv,rough)*smith(nl,rough)*f/(4.0*nv*nl+.001);vec3 diff=(1.0-f)*(1.0-uMetal)*base/PI;return (diff+spec)*c*nl;}
float shade(){if(!uShadowOn||!uReceive)return 1.0;vec3 s=vShadow.xyz/vShadow.w*.5+.5;if(any(lessThan(s,vec3(0)))||any(greaterThan(s,vec3(1))))return 1.0;float occ=0.;vec2 px=1./vec2(textureSize(uShadow,0));for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++){float d=texture(uShadow,s.xy+vec2(x,y)*px*(uPattern>1.5?4.:1.5)).r;occ+=s.z-.002>d?1.:0.;}return 1.-.26*occ/9.;}
void main(){if(uPattern>1.5){vec3 floorColor=backdrop(gl_FragCoord.xy/uViewport);frag=vec4(floorColor*mix(1.,shade(),.56),1.);return;}vec3 n=normalize(vNormal);if(!gl_FrontFacing)n=-n;vec3 v=normalize(uEye-vPosition);vec3 base=pow(uColor*vColor.rgb,vec3(2.2));float rough=clamp(uRough,.15,.98);if(uPattern>.5){float grain=sin(vPosition.x*380.+sin(vPosition.z*65.))*sin(vPosition.z*9.);rough=clamp(rough+.012*grain,.15,.95);}
 vec3 f0=mix(vec3(.045),base,uMetal);float nv=max(dot(n,v),.001);vec3 r=reflect(-v,n);
 vec3 sky=mix(vec3(.20,.27,.34),vec3(.78,.87,.97),clamp(r.y*.5+.5,0.,1.));
 float box1=pow(max(dot(r,normalize(vec3(-.6,.95,.7))),0.),mix(32.,4.,rough));float box2=pow(max(dot(r,normalize(vec3(.7,.4,-.7))),0.),mix(24.,3.,rough));
 vec3 env=sky*.74+vec3(1.7,1.8,1.9)*box1+vec3(.6,.78,.96)*box2;
 vec3 color=base*(1.-uMetal)*(.28+.32*max(n.y,0.)) + env*fresnel(nv,f0)*(.72+.18*uMetal);
 color+=lamp(n,v,normalize(vec3(-.7,1.,.65)),vec3(2.3,2.45,2.6),base,f0,rough)*shade();
 color+=lamp(n,v,normalize(vec3(.85,.65,-.7)),vec3(.68,.87,1.12),base,f0,rough);
 color+=lamp(n,v,normalize(vec3(.4,.15,1.)),vec3(.34,.40,.47),base,f0,rough);
 color+=uSoft*base*(.20+.25*pow(1.-nv,2.));color+=base*uEmission;
 // Neutral photographic shoulder. No bloom, no neon, and no color clipping.
 color=(color*(2.51*color+.03))/(color*(2.43*color+.59)+.14);
 color=pow(clamp(color,0.,1.),vec3(1./2.2));float alpha=uOpacity*vColor.a;
 if(uOpacity<.99)alpha*=.65+.35*pow(1.-nv,1.4);
 frag=vec4(color,alpha);
}`;
const safeVertex = `#version 300 es
precision highp float;
layout(location=0) in vec3 aPosition;layout(location=1) in vec3 aNormal;
layout(location=3) in mat4 aInstance;layout(location=7) in vec4 aColor;
layout(location=8) in mat3 aInstanceNormal;
uniform mat4 uModel,uVP;uniform mat3 uNormal;uniform bool uInstanced;
uniform vec3 uColor,uEye;uniform float uMetal,uRough,uSoft,uEmission;
out vec3 vLit;out float vAlpha;out vec4 vColor;
void main(){mat4 m=uModel;if(uInstanced)m=m*aInstance;vec4 p=m*vec4(aPosition,1.);gl_Position=uVP*p;
 vec3 n=normalize(uNormal*(uInstanced?aInstanceNormal*aNormal:aNormal));vec3 v=normalize(uEye-p.xyz);
 float nv=abs(dot(n,v));vec3 l=normalize(vec3(-.7,1.,.65));float key=max(dot(n,l),0.);
 float fill=max(dot(n,normalize(vec3(.85,.65,-.7))),0.);vec3 r=reflect(-v,n);
 float softbox=pow(max(dot(r,normalize(vec3(-.6,.95,.7))),0.),6.);
 float rim=(1.-nv)*(1.-nv);vColor=uInstanced?aColor:vec4(1.);
 vec3 c=uColor*vColor.rgb;vLit=c*(.43+.38*key+.14*fill+.08*max(n.y,0.));
 vLit+=vec3(.24,.28,.32)*softbox*(.35+.65*uMetal)+rim*vec3(.10,.15,.18)*uMetal;
 vLit+=c*(uSoft*.22+uEmission*.3);vLit=clamp(vLit,0.,1.);vAlpha=.65+.35*rim;
}`;
const safeFragment = `#version 300 es
precision highp float;in vec3 vLit;in float vAlpha;in vec4 vColor;out vec4 frag;
uniform float uOpacity,uPattern;uniform vec2 uViewport;
void main(){if(uPattern>1.5){vec2 p=gl_FragCoord.xy/uViewport;vec2 d=(p-vec2(.57,.62))*vec2(.90,1.);float fall=clamp(length(d)*1.05,0.,1.);frag=vec4(mix(vec3(.979,.985,.990),vec3(.878,.918,.946),fall),1.);return;}
 frag=vec4(vLit,uOpacity*vColor.a*(uOpacity<.99?vAlpha:1.));}`;
const depthFrag = `#version 300 es
precision highp float;out vec4 f;void main(){f=vec4(1.);}`;
const quadV = `#version 300 es
precision highp float;out vec2 uv;void main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);uv=p;gl_Position=vec4(p*2.-1.,0.,1.);}`;
const quadF = `#version 300 es
precision highp float;in vec2 uv;out vec4 frag;uniform sampler2D a,b;uniform float blend;uniform vec2 resolution;
vec4 sampleSoft(sampler2D tex,vec2 p,float rad){vec2 d=rad/resolution;return texture(tex,p)*.4+(texture(tex,p+d)+texture(tex,p-d)+texture(tex,p+vec2(d.x,-d.y))+texture(tex,p+vec2(-d.x,d.y)))*.15;}
void main(){float soft=sin(blend*3.14159)*2.;frag=mix(sampleSoft(a,uv,soft),sampleSoft(b,uv,soft),blend);}`;
const backdropF = `#version 300 es
precision highp float;in vec2 uv;out vec4 frag;
void main(){vec2 d=(uv-vec2(.57,.62))*vec2(.90,1.0);float fall=clamp(length(d)*1.05,0.,1.);frag=vec4(mix(vec3(.979,.985,.990),vec3(.878,.918,.946),fall),1.);}`;
interface Buffers {
    vao: WebGLVertexArrayObject;
    vbo: WebGLBuffer;
    ibo: WebGLBuffer;
    version: number;
}
interface Target {
    fb: WebGLFramebuffer;
    tex: WebGLTexture;
    depth: WebGLRenderbuffer;
}
function normalMatrix(m: Mat4): Float32Array {
    const x = [m[0], m[1], m[2]], y = [m[4], m[5], m[6]], z = [m[8], m[9], m[10]];
    const cross = (a: number[], b: number[]) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    const a = cross(y, z), b = cross(z, x), c = cross(x, y), det = x[0] * a[0] + x[1] * a[1] + x[2] * a[2], inv = Math.abs(det) > 1e-12 ? 1 / det : 0;
    return new Float32Array([...a, ...b, ...c].map(v => v * inv));
}
export class Renderer {
    gl: WebGL2RenderingContext;
    program: WebGLProgram;
    safeProgram: WebGLProgram;
    shadowProgram: WebGLProgram;
    quadProgram: WebGLProgram;
    backgroundProgram: WebGLProgram;
    cache = new WeakMap<Geometry, Buffers>();
    instanceCache = new WeakMap<InstancedMesh, {
        m: WebGLBuffer;
        c: WebGLBuffer;
        n: WebGLBuffer;
        version: number;
    }>();
    uniformCache = new WeakMap<WebGLProgram, Map<string, WebGLUniformLocation | null>>();
    width = 1;
    height = 1;
    ratio = 1;
    drawCalls = 0;
    triangles = 0;
    quality = 'high';
    shadowEnabled = true;
    shadowSize = 1024;
    shadowFB: WebGLFramebuffer;
    shadowTex: WebGLTexture;
    lightVP = multiply(ortho(-11, 11, -11, 11, .1, 40), lookAt([-8, 15, 10], [0, 0, 0]));
    targets: Target[] = [];
    error: string[] = [];
    constructor(public canvas: HTMLCanvasElement) { const gl = canvas.getContext('webgl2', { alpha: true, antialias: true, premultipliedAlpha: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' }); if (!gl)
        throw new Error('WebGL2 is unavailable. Hardware or software WebGL must be enabled.'); this.gl = gl; this.program = this.makeProgram(vertex, fragment); this.safeProgram = this.makeProgram(safeVertex, safeFragment); this.shadowProgram = this.makeProgram(vertex, depthFrag); this.quadProgram = this.makeProgram(quadV, quadF); this.backgroundProgram = this.makeProgram(quadV, backdropF); this.shadowFB = gl.createFramebuffer()!; this.shadowTex = gl.createTexture()!; gl.bindTexture(gl.TEXTURE_2D, this.shadowTex); gl.texImage2D(gl.TEXTURE_2D, 0, gl.DEPTH_COMPONENT24, this.shadowSize, this.shadowSize, 0, gl.DEPTH_COMPONENT, gl.UNSIGNED_INT, null); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); gl.bindFramebuffer(gl.FRAMEBUFFER, this.shadowFB); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.DEPTH_ATTACHMENT, gl.TEXTURE_2D, this.shadowTex, 0); gl.drawBuffers([gl.NONE]); gl.readBuffer(gl.NONE); if (gl.checkFramebufferStatus(gl.FRAMEBUFFER) !== gl.FRAMEBUFFER_COMPLETE)
        this.shadowEnabled = false; gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.enable(gl.DEPTH_TEST); gl.disable(gl.CULL_FACE); this.canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); this.error.push('WebGL context lost'); }); }
    makeProgram(v: string, f: string) { const g = this.gl, p = g.createProgram()!; for (const [type, code] of [[g.VERTEX_SHADER, v], [g.FRAGMENT_SHADER, f]] as [
        number,
        string
    ][]) {
        const s = g.createShader(type)!;
        g.shaderSource(s, code);
        g.compileShader(s);
        if (!g.getShaderParameter(s, g.COMPILE_STATUS))
            throw Error(g.getShaderInfoLog(s) || 'Shader compilation');
        g.attachShader(p, s);
        g.deleteShader(s);
    } g.linkProgram(p); if (!g.getProgramParameter(p, g.LINK_STATUS))
        throw Error(g.getProgramInfoLog(p) || 'Shader linking'); return p; }
    resize(w: number, h: number) { this.ratio = this.quality === 'safe' ? .55 : this.quality === 'medium' ? 1 : Math.min(devicePixelRatio, 1.4); const nw = Math.round(w * this.ratio), nh = Math.round(h * this.ratio); if (nw === this.width && nh === this.height)
        return; this.width = nw; this.height = nh; this.canvas.width = nw; this.canvas.height = nh; this.targets.forEach(t => { this.gl.deleteFramebuffer(t.fb); this.gl.deleteTexture(t.tex); this.gl.deleteRenderbuffer(t.depth); }); this.targets = []; }
    target(i: number) { if (this.targets[i])
        return this.targets[i]; const g = this.gl, fb = g.createFramebuffer()!, tex = g.createTexture()!, depth = g.createRenderbuffer()!; g.bindTexture(g.TEXTURE_2D, tex); g.texImage2D(g.TEXTURE_2D, 0, g.RGBA, this.width, this.height, 0, g.RGBA, g.UNSIGNED_BYTE, null); g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MIN_FILTER, g.LINEAR); g.texParameteri(g.TEXTURE_2D, g.TEXTURE_MAG_FILTER, g.LINEAR); g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_S, g.CLAMP_TO_EDGE); g.texParameteri(g.TEXTURE_2D, g.TEXTURE_WRAP_T, g.CLAMP_TO_EDGE); g.bindRenderbuffer(g.RENDERBUFFER, depth); g.renderbufferStorage(g.RENDERBUFFER, g.DEPTH_COMPONENT16, this.width, this.height); g.bindFramebuffer(g.FRAMEBUFFER, fb); g.framebufferTexture2D(g.FRAMEBUFFER, g.COLOR_ATTACHMENT0, g.TEXTURE_2D, tex, 0); g.framebufferRenderbuffer(g.FRAMEBUFFER, g.DEPTH_ATTACHMENT, g.RENDERBUFFER, depth); return this.targets[i] = { fb, tex, depth }; }
    bindGeometry(mesh: Mesh) {
        const g = this.gl, geo = mesh.geometry;
        let b = this.cache.get(geo);
        if (!b) {
            b = { vao: g.createVertexArray()!, vbo: g.createBuffer()!, ibo: g.createBuffer()!, version: -1 };
            this.cache.set(geo, b);
            g.bindVertexArray(b.vao);
            g.bindBuffer(g.ARRAY_BUFFER, b.vbo);
            g.bufferData(g.ARRAY_BUFFER, geo.data, g.DYNAMIC_DRAW);
            for (const [location, size, offset] of [[0, 3, 0], [1, 3, 12], [2, 2, 24]]) {
                g.enableVertexAttribArray(location);
                g.vertexAttribPointer(location, size, g.FLOAT, false, 32, offset);
            }
            g.bindBuffer(g.ELEMENT_ARRAY_BUFFER, b.ibo);
            g.bufferData(g.ELEMENT_ARRAY_BUFFER, geo.indices, g.STATIC_DRAW);
            b.version = geo.version;
        }
        else {
            g.bindVertexArray(b.vao);
            if (b.version !== geo.version) {
                g.bindBuffer(g.ARRAY_BUFFER, b.vbo);
                g.bufferSubData(g.ARRAY_BUFFER, 0, geo.data);
                b.version = geo.version;
            }
        }
        if (mesh instanceof InstancedMesh) {
            let ib = this.instanceCache.get(mesh);
            if (!ib) {
                ib = { m: g.createBuffer()!, c: g.createBuffer()!, n: g.createBuffer()!, version: -1 };
                this.instanceCache.set(mesh, ib);
            }
            g.bindBuffer(g.ARRAY_BUFFER, ib.m);
            if (ib.version !== mesh.instanceVersion)
                g.bufferData(g.ARRAY_BUFFER, mesh.matrices, g.DYNAMIC_DRAW);
            for (let i = 0; i < 4; i++) {
                g.enableVertexAttribArray(3 + i);
                g.vertexAttribPointer(3 + i, 4, g.FLOAT, false, 64, i * 16);
                g.vertexAttribDivisor(3 + i, 1);
            }
            g.bindBuffer(g.ARRAY_BUFFER, ib.c);
            if (ib.version !== mesh.instanceVersion)
                g.bufferData(g.ARRAY_BUFFER, mesh.colors, g.DYNAMIC_DRAW);
            g.enableVertexAttribArray(7);
            g.vertexAttribPointer(7, 4, g.FLOAT, false, 16, 0);
            g.vertexAttribDivisor(7, 1);
            g.bindBuffer(g.ARRAY_BUFFER, ib.n);
            if (ib.version !== mesh.instanceVersion)
                g.bufferData(g.ARRAY_BUFFER, mesh.normals, g.DYNAMIC_DRAW);
            for (let i = 0; i < 3; i++) {
                g.enableVertexAttribArray(8 + i);
                g.vertexAttribPointer(8 + i, 3, g.FLOAT, false, 36, i * 12);
                g.vertexAttribDivisor(8 + i, 1);
            }
            ib.version = mesh.instanceVersion;
        }
        else
            for (let i = 3; i <= 10; i++) {
                g.disableVertexAttribArray(i);
                g.vertexAttribDivisor(i, 0);
            }
    }
    uniform(p: WebGLProgram, n: string) { let map = this.uniformCache.get(p); if (!map) {
        map = new Map();
        this.uniformCache.set(p, map);
    } if (!map.has(n))
        map.set(n, this.gl.getUniformLocation(p, n)); return map.get(n)!; }
    draw(mesh: Mesh, p: WebGLProgram, depth = false) { const g = this.gl; this.bindGeometry(mesh); g.uniformMatrix4fv(this.uniform(p, 'uModel'), false, mesh.world); g.uniform1i(this.uniform(p, 'uInstanced'), mesh instanceof InstancedMesh ? 1 : 0); if (!depth) {
        g.uniformMatrix3fv(this.uniform(p, 'uNormal'), false, normalMatrix(mesh.world));
        const m = mesh.material;
        g.uniform3fv(this.uniform(p, 'uColor'), m.color);
        for (const [n, v] of [['uMetal', m.metalness], ['uRough', m.roughness], ['uOpacity', m.opacity], ['uEmission', m.emission], ['uSoft', m.softness], ['uPattern', m.patterned]] as [
            string,
            number
        ][])
            g.uniform1f(this.uniform(p, n), v);
        g.uniform1i(this.uniform(p, 'uReceive'), mesh.receiveShadow ? 1 : 0);
    } const count = mesh.geometry.indices.length; if (mesh instanceof InstancedMesh) {
        g.drawElementsInstanced(g.TRIANGLES, count, g.UNSIGNED_INT, 0, mesh.count);
        this.triangles += count / 3 * mesh.count;
    }
    else {
        g.drawElements(g.TRIANGLES, count, g.UNSIGNED_INT, 0);
        this.triangles += count / 3;
    } this.drawCalls++; }
    render(root: Node, camera: CameraRig, target: WebGLFramebuffer | null = null) {
        const g = this.gl, colorProgram = this.quality === 'safe' ? this.safeProgram : this.program;
        root.update();
        camera.update();
        const opaque: Mesh[] = [], transparent: Mesh[] = [];
        root.traverse(n => { if (n instanceof Mesh && n.material.opacity > .002)
            ((n.material.opacity > .995 && !(n instanceof InstancedMesh && Array.from({length:n.count},(_,i)=>n.colors[i*4+3]).some(a=>a<.995))) ? opaque : transparent).push(n); });
        transparent.sort((a, b) => transform(camera.view, [a.world[12], a.world[13], a.world[14]])[2] - transform(camera.view, [b.world[12], b.world[13], b.world[14]])[2]);
        const shadow = this.shadowEnabled && this.quality === 'high';
        g.enable(g.DEPTH_TEST);
        g.depthMask(true);
        g.disable(g.BLEND);
        if (shadow) {
            g.bindFramebuffer(g.FRAMEBUFFER, this.shadowFB);
            g.viewport(0, 0, this.shadowSize, this.shadowSize);
            g.clear(g.DEPTH_BUFFER_BIT);
            g.useProgram(this.shadowProgram);
            g.uniformMatrix4fv(this.uniform(this.shadowProgram, 'uVP'), false, this.lightVP);
            g.uniformMatrix4fv(this.uniform(this.shadowProgram, 'uLight'), false, this.lightVP);
            for (const m of opaque)
                if (m.castShadow)
                    this.draw(m, this.shadowProgram, true);
        }
        g.bindFramebuffer(g.FRAMEBUFFER, target);
        g.viewport(0, 0, this.width, this.height);
        g.clearColor(0, 0, 0, 0);
        g.clear(g.COLOR_BUFFER_BIT | g.DEPTH_BUFFER_BIT);
        g.disable(g.DEPTH_TEST);
        g.bindVertexArray(null);
        g.useProgram(this.backgroundProgram);
        g.drawArrays(g.TRIANGLES, 0, 3);
        g.enable(g.DEPTH_TEST);
        g.useProgram(colorProgram);
        g.uniform2f(this.uniform(colorProgram, 'uViewport'), this.width, this.height);
        g.uniformMatrix4fv(this.uniform(colorProgram, 'uVP'), false, camera.vp);
        g.uniformMatrix4fv(this.uniform(colorProgram, 'uLight'), false, this.lightVP);
        g.uniform3fv(this.uniform(colorProgram, 'uEye'), camera.state.position);
        g.uniform1i(this.uniform(colorProgram, 'uShadowOn'), shadow ? 1 : 0);
        g.activeTexture(g.TEXTURE0);
        g.bindTexture(g.TEXTURE_2D, this.shadowTex);
        g.uniform1i(this.uniform(colorProgram, 'uShadow'), 0);
        for (const m of opaque)
            this.draw(m, colorProgram);
        g.enable(g.BLEND);
        g.blendFuncSeparate(g.SRC_ALPHA, g.ONE_MINUS_SRC_ALPHA, g.ONE, g.ONE_MINUS_SRC_ALPHA);
        g.depthMask(false);
        for (const m of transparent)
            this.draw(m, colorProgram);
        g.depthMask(true);
        g.disable(g.BLEND);
        g.bindVertexArray(null);
    }
    frame(root: Node, camera: CameraRig, other?: {
        root: Node;
        camera: CameraRig;
        blend: number;
    }) { this.drawCalls = 0; this.triangles = 0; if (!other || other.blend <= 0) {
        this.render(root, camera);
        return;
    } if (other.blend >= 1) {
        this.render(other.root, other.camera);
        return;
    } const a = this.target(0), b = this.target(1); this.render(root, camera, a.fb); this.render(other.root, other.camera, b.fb); const g = this.gl; g.bindFramebuffer(g.FRAMEBUFFER, null); g.viewport(0, 0, this.width, this.height); g.disable(g.DEPTH_TEST); g.useProgram(this.quadProgram); g.activeTexture(g.TEXTURE0); g.bindTexture(g.TEXTURE_2D, a.tex); g.uniform1i(this.uniform(this.quadProgram, 'a'), 0); g.activeTexture(g.TEXTURE1); g.bindTexture(g.TEXTURE_2D, b.tex); g.uniform1i(this.uniform(this.quadProgram, 'b'), 1); g.uniform1f(this.uniform(this.quadProgram, 'blend'), other.blend); g.uniform2f(this.uniform(this.quadProgram, 'resolution'), this.width, this.height); g.bindVertexArray(null); g.drawArrays(g.TRIANGLES, 0, 3); }
    diagnostics() { const g = this.gl, e = g.getError(), ext = g.getExtension('WEBGL_debug_renderer_info'); return { backend: 'native WebGL2 / TypeScript', renderer: ext ? g.getParameter(ext.UNMASKED_RENDERER_WEBGL) : g.getParameter(g.RENDERER), webgl: g.getParameter(g.VERSION), drawCalls: this.drawCalls, triangles: this.triangles, width: this.width, height: this.height, quality: this.quality, glError: e, errors: this.error }; }
}
