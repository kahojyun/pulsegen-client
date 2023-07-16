Instruction API
===============

.. currentmodule:: pulsegen_client.pulse

Instruction API 通过一系列的指令控制波形的生成，目前支持的指令有：

:class:`Play`
    在给定时间点在指定通道上添加波形

:class:`ShiftPhase`
    偏置指定通道的相位

:class:`SetPhase`
    在给定时间点设置指定通道的相位

:class:`ShiftFrequency`
    在给定时间点偏置指定通道的频率

:class:`SetFrequency`
    在给定时间点设置指定通道的频率

:class:`SwapPhase`
    在给定时间点交换两个通道的相位


使用示例如下：

.. literalinclude:: ../example/simple.py
    :language: python3
    :linenos:


相位计算
--------

目前程序会记录三种频率：通道的载波频率 :math:`f_c`，由于频率偏置而产生的额外频率 :math:`f_a`，以及 :class:`Play` 指令中的附加频率 :math:`f_p`。前两者相加得到全局频率 :math:`f`，即 :math:`f = f_c + f_a`。相位则记录两种：通道的初相位 :math:`\phi_0` 与 :class:`Play` 指令中的附加相位 :math:`\phi_p`。利用这些信息可以计算出时刻 :math:`t` 的额外相位 :math:`\phi_a(t)`：

.. math::

    \phi_a(t) = 2\pi f_a t + \phi_0

载波相位 :math:`\phi_c(t)`：

.. math::

    \phi_c(t) = \phi_a(t) + 2\pi f_c t = 2\pi f t + \phi_0

起始时刻为 :math:`\tau` 的波形中的相位 :math:`\phi_p(t)` 则为：

.. math::

    \phi_p(t) = \phi_c(t) + 2\pi f_p (t - \tau)

目前 :class:`ShiftFrequency` 指令与 :class:`SetFrequency` 指令改变的是 :math:`f_a`，并且会令额外相位 :math:`\phi_a(t)` 在给定时刻 :math:`\tau` 连续：

.. math::

    \phi_a(\tau) = 2\pi f_a \tau + \phi_0 = \phi_a'(\tau) = 2\pi f_a' \tau +
    \phi_0'

:class:`ShiftPhase` 指令无时间参数，直接改变 :math:`\phi_0`。:class:`SetPhase` 改变 :math:`\phi_0` 使得给定时刻 :math:`\tau` 的额外相位 :math:`\phi_a(\tau)` 变为给定值 :math:`\phi`：

.. math::

    \phi_a'(\tau) = 2\pi f_a \tau + \phi_0' = \phi

:class:`SwapPhase` 指令在给定时刻 :math:`\tau` 交换两个通道的载波相位 :math:`\phi_c^{(1)}(\tau)` 与 :math:`\phi_c^{(2)}(\tau)`：

.. math::

    \phi_c^{(1)'}(\tau) = \phi_c^{(2)}(\tau) \\
    \phi_c^{(2)'}(\tau) = \phi_c^{(1)}(\tau)


波形对齐
--------

程序在采样包络时会对波形进行对齐，即将波形的起始点对齐到某个单位时间的整数倍。对齐参数在 :meth:`RequestBuilder.add_channel` 的 ``align_level`` 中指定，假设给定值为 :math:`n`，采样间隔为 :math:`\Delta t`，则对齐的单位时间为 :math:`2^n\Delta t`，比如 ``align_level`` 为 -4，则单位时间为 :math:`2^{-4}\Delta t`，即 :math:`\Delta t / 16`。


执行顺序
--------

.. warning:: 

    按照指令的添加顺序执行而不是按照指令附带的时间参数顺序执行。


计算结果
--------

目前程序会返回一个字典，键为通道名，值为一个元组，元组中的第一个元素为 I 通道的采样值，第二个元素为 Q 通道的采样值。
