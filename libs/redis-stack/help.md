* Host: localhost (或者直接点自动发现出的容器 IP)。
* Port: 6379 (注意：在容器内部，它永远是 6379)。
* Username: default。
* Password: root123。
 
* 这种情况通常是开启了 RedisInsight 的安全访问。如果你没有在环境变量里设置过 RIPASSWORD 之类的参数，它通常是不应该出现的。如果出现了，尝试：
* 用户名留空，只输密码 root123。
* 或者用户名填 default，密码填 root123。

http://localhost:8002  redis web ui

