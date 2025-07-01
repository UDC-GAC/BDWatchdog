#!/usr/bin/env bash
# Run in the opentsdb installation folder

METRICS=(
  # SYSTEM POWER CONSUMPTION AND TEMP
  #Core
  sys.core.temp
  #Chip (processor or package)
  sys.cpu.temp
  sys.cpu.energy
  #System
  sys.processors.temp
  sys.processors.energy
  #Process - Generated through system cpu and energy, and process cpu
  proc.cpu.energy
  # SYSTEM METRICS
  #cpu
  sys.cpu.kernel
  sys.cpu.user
  sys.cpu.idle
  sys.cpu.wait
  #CPU
  sys.cpu.usage
  #DISK
  sys.disk.usage
  sys.disk.read.ios
  sys.disk.read.mb
  sys.disk.write.ios
  sys.disk.write.mb
  #MEM
  sys.mem.free
  sys.mem.usage
  #NET
  sys.net.in.mb
  sys.net.out.mb
  sys.net.usage
  # PROCESS METRICS
  #CPU
  proc.cpu.user
  proc.cpu.kernel
  #DISK
  proc.disk.reads.mb
  proc.disk.writes.mb
  #MEM
  proc.mem.virtual
  proc.mem.resident
  proc.mem.swap
  #SWAP
  sys.swap.free
  # NET
  proc.net.tcp.out.mb
  proc.net.tcp.out.packets
  proc.net.tcp.in.mb
  proc.net.tcp.in.packets
  proc.net.udp.out.mb
  proc.net.udp.out.packets
  proc.net.udp.in.mb
  proc.net.udp.in.packets
)

./build/tsdb mkmetric "${METRICS[@]}"