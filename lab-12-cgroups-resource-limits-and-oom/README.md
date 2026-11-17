# LAB-DOC-12 — Kaynak Limitleri (cgroups v2) ve OOMKilled Teşhisi

| Profil / Araçlar | Açık Portlar |
|---|---|
| `docker run --cpus/--memory`, `docker stats`, `docker update`, `alpine:3.20`, Python stres uygulaması | — |

## Amaç

- Limitsiz bir container'ın sunucunun CPU ve belleğini tüketebildiğini görmek.
- `--cpus` ve `--memory` limitlerini koyup ölçmek; OOMKilled (137) durumunu görmek.
- Limitlerin cgroup v2 dosyalarına nasıl yazıldığını incelemek.
- Limitleri `docker update` ile değiştirmek.

## Ön Koşullar

- Sunucuda cgroup v2 etkin olmalıdır (`docker info | grep "Cgroup Version"` çıktısı `2`).

## Adım Adım Uygulama Rehberi

### 1. Limitsiz CPU Tüketimi

```bash
cd ~/docker-labs/lab-12-cgroups-resource-limits-and-oom
```

```bash
docker info --format 'Cgroup surumu: {{.CgroupVersion}}, CPU: {{.NCPU}}'
```

Bir çekirdeği tamamen kullanan, limitsiz bir container:

```bash
docker run -d --name cpu-unlimited alpine:3.20 sh -c 'while :; do :; done'
```

```bash
docker stats --no-stream --format '{{.Name}} CPU={{.CPUPerc}}' cpu-unlimited
```

`CPU` değeri yaklaşık `100%` olur (bir çekirdeğin tamamı).

### 2. CPU Kotası

Aynı yükü yarım çekirdekle sınırlayın:

```bash
docker run -d --name cpu-limited --cpus=0.5 alpine:3.20 sh -c 'while :; do :; done'
```

```bash
docker stats --no-stream --format '{{.Name}} CPU={{.CPUPerc}}' cpu-unlimited cpu-limited
```

`cpu-limited` yaklaşık `50%` değerinde kalır. Kotanın cgroup dosyasındaki karşılığı:

```bash
docker exec cpu-limited cat /sys/fs/cgroup/cpu.max
```

`50000 100000`: her 100 ms'lik dönemde en fazla 50 ms CPU zamanı.

Limiti container'ı durdurmadan değiştirin:

```bash
docker update --cpus=0.2 cpu-limited
```

```bash
docker stats --no-stream --format '{{.Name}} CPU={{.CPUPerc}}' cpu-limited
```

```bash
docker rm -f cpu-unlimited cpu-limited
```

### 3. Bellek Limiti ve cgroup Dosyası

```bash
docker run -d --name mem-limited --memory=128m --memory-swap=128m nginx:alpine
```

```bash
docker exec mem-limited cat /sys/fs/cgroup/memory.max
```

```bash
docker stats --no-stream --format '{{.Name}} MEM={{.MemUsage}}' mem-limited
```

`MemUsage` sütununda limit `128MiB` olarak görünür.

### 4. Bellek Sızıntısı ve OOMKilled

Her saniye 25 MB bellek ayıran stres uygulamasını inceleyin ve build edin:

```bash
cat stress-app/stress.py
```

```bash
docker build -t oom-stress:1.0 stress-app/
```

50 MB limitle çalıştırın. Uygulama ikinci veya üçüncü adımda limiti aşar:

```bash
docker run --name stress-victim --memory=50m --memory-swap=50m oom-stress:1.0
```

```bash
docker ps -a --filter name=stress-victim --format '{{.Names}} {{.Status}}'
```

```bash
docker inspect -f 'OOMKilled={{.State.OOMKilled}} ExitCode={{.State.ExitCode}}' stress-victim
```

`137 = 128 + 9`: süreç SIGKILL (9) ile sonlandırıldı. Uygulama kendi hatasıyla değil, çekirdek tarafından öldürüldü; bu yüzden uygulama logunda hata satırı yoktur.

Çekirdek kaydında OOM olayını görün:

```bash
sudo dmesg -T | grep -iE "memory cgroup out of memory|oom-kill" | tail -n 3
```

### 5. OOM ve Restart Politikası

Restart politikası OOM sorununu çözmez, yalnızca döngüye sokar:

```bash
docker run -d --name stress-loop --memory=50m --memory-swap=50m --restart on-failure:3 oom-stress:1.0
```

```bash
sleep 20
```

```bash
docker inspect -f 'restarts={{.RestartCount}} OOMKilled={{.State.OOMKilled}} status={{.State.Status}}' stress-loop
```

Kalıcı çözüm: uygulamanın bellek kullanımını düzeltmek veya limiti gerçek ihtiyaca göre artırmak.

## Temizlik

```bash
docker rm -f cpu-unlimited cpu-limited mem-limited stress-victim stress-loop 2>/dev/null || true
```

```bash
docker rmi oom-stress:1.0 2>/dev/null || true
```
