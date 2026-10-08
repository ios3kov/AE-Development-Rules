// Original offline C++17 teaching fixture. No Adobe SDK interfaces or certification.
#pragma once
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <limits>
#include <optional>
#include <string_view>

namespace ae_rules_example {
struct FrameCount { double value; };
struct FrameRate { double frames_per_second; };
struct Seconds { double value; };
inline std::optional<Seconds> to_seconds(FrameCount f, FrameRate fps) {
    if (!std::isfinite(f.value) || !std::isfinite(fps.frames_per_second) || fps.frames_per_second <= 0) return {};
    const double seconds = f.value / fps.frames_per_second;
    if (!std::isfinite(seconds)) return {};
    return Seconds{seconds};
}

// Bounds check precedes every addition/multiplication and buffer address calculation.
inline std::optional<std::size_t> pixel_offset(std::size_t x, std::size_t y,
    std::size_t width, std::size_t height, std::size_t stride, std::size_t capacity) {
#ifdef DEMONSTRATE_ORIGINAL_DEFECT
    if (x > width || y >= height) return {}; // Original off-by-one boundary defect.
#else
    if (x >= width || y >= height) return {};
#endif
    constexpr auto max = std::numeric_limits<std::size_t>::max();
    if (width > max / 4 || stride < width * 4 || y > max / stride || x > max / 4) return {};
    const auto row = y * stride, col = x * 4;
    if (row > max - col) return {};
    const auto offset = row + col;
    if (offset > capacity || capacity - offset < 4) return {};
    return offset;
}

// Explicit RGBA8 conversion; 16bpc and float HDR are separate contracts, not clipped here.
inline std::optional<double> rgba8_to_unit(unsigned channel) {
    if (channel > 255) return {};
    return channel / 255.0;
}

// Strict bounded decimal parser for a small state/protocol field; no atoi, truncation or overflow.
inline std::optional<std::uint32_t> parse_count(std::string_view input) {
    if (input.empty() || input.size() > 10) return {};
    std::uint32_t value = 0;
    for (unsigned char c : input) {
        if (c < '0' || c > '9') return {};
        const auto digit = static_cast<std::uint32_t>(c - '0');
        if (value > (std::numeric_limits<std::uint32_t>::max() - digit) / 10) return {};
        value = value * 10 + digit;
    }
    return value;
}

enum class State { idle, acquired, canceled };
enum class Event { acquire, release, cancel, reset };
inline std::optional<State> transition(State state, Event event) {
    if (event == Event::cancel) return State::canceled;
    if (state == State::canceled && event == Event::reset) return State::idle;
    if (state == State::idle && event == Event::acquire) return State::acquired;
    if (state == State::acquired && event == Event::release) return State::idle;
    return {};
}

// One owner, exactly once release, deterministic error-path cleanup. Not an AE checkout/checkin mock.
class Lease {
    int* releases_;
public:
    explicit Lease(int& releases) : releases_(&releases) {}
    Lease(const Lease&) = delete;
    Lease& operator=(const Lease&) = delete;
    Lease(Lease&& other) noexcept : releases_(other.releases_) { other.releases_ = nullptr; }
    Lease& operator=(Lease&&) = delete;
    ~Lease() { if (releases_) ++*releases_; }
};
}
