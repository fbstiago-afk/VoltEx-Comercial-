# -*- coding: utf-8 -*-
CSS = r"""
*{box-sizing:border-box}
html,body{margin:0!important;padding:0!important;overflow:hidden!important}
::-webkit-scrollbar{width:0!important;height:0!important;display:none}
.vx{font-family:'Segoe UI',Arial,sans-serif;color:#F2F4F5;line-height:1.35}
@keyframes up{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
@keyframes left{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.6)}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
.ov{font-size:10px;font-weight:600;letter-spacing:.14em;color:#FF8C00;text-transform:uppercase}
.tt{font-size:22px;font-weight:600;color:#F2F4F5;margin-top:1px;animation:left .5s ease-out both}
.hd{display:flex;justify-content:space-between;align-items:flex-end;gap:24px}
.chips{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px;align-items:center;max-width:62%}
.chip{padding:3px 10px;border-radius:999px;background:rgba(255,140,0,.14);color:#FFB45C;font-size:11px;font-weight:600;white-space:nowrap}
.per{font-size:11px;color:#9AA6B0;margin-right:4px;white-space:nowrap}
.mut{color:#7D8A95}
.up{color:#3FB68B;font-weight:600}.dn{color:#FF6B6F;font-weight:600}.wa{color:#F2B84B;font-weight:600}.ac{color:#FF8C00;font-weight:600}
.kb{display:flex;align-items:stretch}
.k{flex:1;min-width:0;padding:4px 18px 0 18px;border-left:1px solid #34404A;animation:up .5s cubic-bezier(.2,.7,.2,1) both}
.k:first-child{border-left:none;padding-left:0}
.k:nth-child(2){animation-delay:.05s}.k:nth-child(3){animation-delay:.1s}.k:nth-child(4){animation-delay:.15s}.k:nth-child(5){animation-delay:.2s}
.kl{font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:#9AA6B0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kv{font-size:28px;font-weight:600;line-height:1.15;margin-top:5px;font-variant-numeric:tabular-nums;color:#F2F4F5;white-space:nowrap}
.kv small,.pv small{font-size:12px;color:#9AA6B0;font-weight:400;margin-left:4px}
.k:hover .kv{color:#FF8C00;transition:color .2s}
.ks{font-size:11px;color:#9AA6B0;margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ins{display:flex;align-items:center;gap:14px;font-size:13px;color:#C9D3DB;animation:up .6s ease-out both}
.ins b{color:#F2F4F5;font-weight:600}
.dot{width:8px;height:8px;border-radius:50%;background:#FF8C00;flex:none;animation:pulse 2.4s ease-in-out infinite}
.src{margin-left:auto;font-size:10px;color:#7D8A95;white-space:nowrap;padding-left:16px}
.pcs{display:flex;gap:0}
.pc{flex:1;min-width:0;display:flex;gap:8px;align-items:center;padding:0 10px;border-left:1px solid #34404A;animation:up .5s ease-out both}
.pc:first-child{border-left:none;padding-left:0}
.pc img{width:52px;height:46px;flex:none;object-fit:contain;filter:drop-shadow(0 6px 8px rgba(0,0,0,.5));animation:float 4s ease-in-out infinite}
.pc:nth-child(even) img{animation-delay:-2s}
.pn{font-size:12px;font-weight:600;color:#F2F4F5;white-space:nowrap}
.pv{font-size:18px;font-weight:600;color:#F2F4F5;font-variant-numeric:tabular-nums;white-space:nowrap}
.tt2{padding:14px 16px;animation:up .3s ease-out both}
.tb{display:grid;grid-template-columns:96px 1fr 40px;gap:8px;align-items:center;font-size:11px;color:#C9D3DB;margin-top:6px}
.tb b{text-align:right;color:#F2F4F5}
.tr{height:6px;background:#34404A;border-radius:3px;overflow:hidden}
.tr i{display:block;height:100%;background:#FF8C00;border-radius:3px;transform-origin:left;animation:grow .7s cubic-bezier(.2,.7,.2,1) both}
.tf{display:flex;justify-content:space-between;gap:10px;margin-top:12px;padding-top:10px;border-top:1px solid #34404A;font-size:11px;color:#9AA6B0}
.tf b{color:#F2F4F5;font-size:13px}
.av{width:44px;height:44px;border-radius:50%;background:rgba(255,140,0,.16);color:#FF8C00;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:16px;flex:none}
.timg{width:96px;height:80px;object-fit:contain;filter:drop-shadow(0 8px 10px rgba(0,0,0,.55));flex:none}
.stk{display:flex;height:14px;border-radius:3px;overflow:hidden;margin:12px 0 14px}
.stk i{display:block;height:100%;transform-origin:left;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
.dr{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid #2C363E;font-size:12px;color:#C9D3DB}
.dr.tot{border-bottom:none;border-top:1px solid #FF8C00;margin-top:6px;font-weight:600;color:#F2F4F5}
.dl{display:flex;align-items:center;gap:10px}
.dv{font-variant-numeric:tabular-nums;font-weight:600;color:#F2F4F5}
.sw{width:10px;height:10px;border-radius:2px;display:inline-block}
.nt{font-size:10px;color:#7D8A95;margin-top:14px;line-height:1.5}
.cv-ov{font-size:11px;font-weight:600;letter-spacing:.2em;color:#FF8C00}
.cv-t{font-size:46px;font-weight:700;line-height:1.05;color:#F2F4F5;margin-top:14px;letter-spacing:-.01em;animation:left .7s ease-out both}
.cv-t span{color:#FF8C00}
.cv-s{font-size:15px;color:#9AA6B0;margin-top:16px;max-width:430px;line-height:1.5;animation:up .8s .15s ease-out both}
.cv-l{display:flex;gap:18px;margin-top:26px;font-size:11px;color:#C9D3DB;letter-spacing:.06em;animation:up .8s .3s ease-out both}
.cv-l div{border-left:2px solid #FF8C00;padding-left:8px}
"""
CSS += r"""
.bl{color:#5B8DB8;font-weight:600}
.rk{display:grid;grid-template-columns:1fr 110px 74px;gap:10px;align-items:center;padding:7px 0;border-bottom:1px solid #2C363E;font-size:12px;color:#C9D3DB;animation:up .5s ease-out both}
.rk b{text-align:right;color:#F2F4F5;font-variant-numeric:tabular-nums;font-weight:600}
.rn{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#F2F4F5}
.rn span{display:block;font-size:10px;color:#7D8A95;margin-top:1px}
.rk:nth-child(3){animation-delay:.04s}.rk:nth-child(4){animation-delay:.08s}.rk:nth-child(5){animation-delay:.12s}.rk:nth-child(6){animation-delay:.16s}
.kb.k6 .k{padding:4px 14px 0 14px}.kb.k6 .kv{font-size:25px}
"""
