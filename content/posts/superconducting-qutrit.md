+++
title = '超导 qutrit：第三能级能算什么，不能算什么'
date = '2026-10-24T13:10:00+08:00'
draft = false
slug = 'superconducting-qutrit'
tags = ['Qutrit', '超导量子计算', '量子力学', '误差缓解', '新易']
description = '根据 2024 年三 qutrit 实验和 2025 年综述，说明第三能级的计算用途与噪声代价。'
images = ['/images/xin-yi-quantum-og.svg']
+++

> 物理部分来自论文摘要和综述。与新易三态的对照写在文末，并保持为对照。

# 超导 qutrit：第三能级能算什么，不能算什么

transmon 是一种超导人工原子。它的势能取得比较平坦，电荷噪声对能级的影响被压低，所以适合做量子比特。能级并不只有两个。|2⟩ 以上的状态通常被当成泄漏：计算本该留在 |0⟩ 和 |1⟩ 里，脉冲太强或失谐不对，布居就跑出去。qutrit 计算反其道而行，把 |2⟩ 收进计算空间，用三个能级编码。

一个 qutrit 的状态空间是三维的。两个 qutrit 是九维，三个是二十七维。同样个数的 qubit 只有八维。仿真自旋为 1 的格点、用更高维压缩某些多比特门、以及一部分量子通信协议，都用得着这多出来的维数。Goss 等人在 2024 年的论文里列举了这些方向，也包括用 qutrit 改善读出、以及理论上更高的纠错阈值。列举是研究议程，不是同一台机器已经全部做成。

代价写在同一篇论文的开头。qudit 的错误种类更多，对噪声更敏感，因此难扩展。他们在固定频率的 transmon 上控制三个 qutrit，把随机编译和无噪声输出外推推广到三能级线路。随机编译把相干噪声搅成更容易用统计处理的随机泡利型通道。外推则在可调的噪声强度上测量，再推回噪声较小的期望值。实验对象包括三 qutrit GHZ 态的层析，以及两到三个 qutrit 的随机线路采样。论文给出的改善最高约三倍，并说明据他们所知，这是第一次在 qutrit 上做的误差缓解。

2025 年的超导量子计算综述把 qudit 和玻色编码、fluxonium 放在同一节的进展里，后面紧跟着扩展规模时的困难。读这两份文献，比较稳妥的句子是：第三能级已经能在少量 transmon 上参加计算，误差缓解对这种小系统有效；它还不是一条已经越过容错阈值的三进制量子计算机路线。

新易把阴、炁、阳配到三个符号上，有时再配到 |0⟩、|1⟩、|2⟩。配得上的是维数：都是 3。配不上的是哈密顿量、脉冲和读出。transmon 的 |1⟩ 与 |2⟩ 之间有非谐性，驱动频率和泄漏通道都要单独标定。卦爻没有这些参数。用 qutrit 的维数给九卦或八十一卦编号，可以得到一张整齐的对照表。用今天的三 qutrit 实验为某次占断背书，实验里没有这项数据。

## 参考文献

- Goss, N. 等. Extending the computational reach of a superconducting qutrit processor. *npj Quantum Information*, 2024. https://www.nature.com/articles/s41534-024-00892-z （访问于 2026-10-24）
- Advancements in superconducting quantum computing. *National Science Review*, 2025, nwaf246. https://academic.oup.com/nsr/article/12/8/nwaf246/8165689 （访问于 2026-10-24）
