#pragma once

#if defined(_NVHPC_STDPAR_GPU)
  #include <cuda/atomic>
template <typename T>
using atomic = cuda::atomic<T, cuda::thread_scope_system>;
template <typename T>
using atomic_ref                           = cuda::atomic_ref<T, cuda::thread_scope_system>;
inline constexpr auto memory_order_relaxed = cuda::memory_order_relaxed;
inline constexpr auto memory_order_acquire = cuda::memory_order_acquire;
inline constexpr auto memory_order_release = cuda::memory_order_release;
inline constexpr auto memory_order_acq_rel = cuda::memory_order_acq_rel;
#else  // _NVHPC_STDPAR_GPU
  #include <atomic>
template <typename T>
using atomic = std::atomic<T>;
template <typename T>
using atomic_ref                           = std::atomic_ref<T>;
inline constexpr auto memory_order_relaxed = std::memory_order_relaxed;
inline constexpr auto memory_order_acquire = std::memory_order_acquire;
inline constexpr auto memory_order_release = std::memory_order_release;
inline constexpr auto memory_order_acq_rel = std::memory_order_acq_rel;
#endif  // _NVHPC_STDPAR_GPU
