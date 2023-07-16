Quick Start Guide
=================

Installation
------------

配置 Server
^^^^^^^^^^^^

#.  安装 `.NET 7.0 SDK <https://dotnet.microsoft.com/en-us/download>`_
#.  运行 `Qynit.PulseGen.Server <https://github.com/kahojyun/Qynit.PulseGen>`_

    .. code-block:: console

        $ git clone https://github.com/kahojyun/Qynit.PulseGen.git
        $ cd Qynit.PulseGen
        $ dotnet run -p Qynit.PulseGen.Server --urls http://localhost:5000


安装 Client
^^^^^^^^^^^^

#.  安装 Python 3.8 及以上版本
#.  安装 ``pulsegen_client``

    .. code-block:: console

        $ git clone https://github.com/kahojyun/pulsegen-client.git
        $ cd pulsegen-client
        $ pip install .
        $ pip install matplotlib


Example
-------

.. literalinclude:: ../example/schedule.py
    :language: python3
    :linenos:
