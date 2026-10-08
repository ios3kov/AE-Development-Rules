#include "native_core.hpp"
#include <iostream>
#include <random>
#include <string>
#include <type_traits>
#include <utility>
using namespace ae_rules_example;
static int failures = 0;
static void check(bool value, const char* name) { if (!value) { std::cerr << name << '\n'; ++failures; } }
int main(int argc, char** argv) {
    static_assert(!std::is_copy_constructible_v<Lease>, "ownership is unique");
    static_assert(!std::is_convertible_v<FrameCount, Seconds>, "frames are not seconds");
    // Original defect: x==width in a padded row was accepted. The same assertion runs both builds.
    check(!pixel_offset(2, 0, 2, 1, 16, 16), "REGRESSION:x-equals-width");
    if (argc == 2 && std::string(argv[1]) == "--regression-only") return failures ? 1 : 0;
    check(!pixel_offset(0, 0, 1, 1, 0, 4), "zero stride");
    check(!pixel_offset(0, 0, SIZE_MAX, 1, SIZE_MAX, SIZE_MAX), "width overflow");
    check(!pixel_offset(0, SIZE_MAX - 1, 1, SIZE_MAX, 8, SIZE_MAX), "row overflow");
    check(!pixel_offset(0, 1, 1, 2, 8, 9), "capacity boundary");
    check(!to_seconds({1}, {0}) && !to_seconds({INFINITY}, {24}), "time nonfinite/zero rate");
    check(rgba8_to_unit(0).value() == 0 && rgba8_to_unit(255).value() == 1 && !rgba8_to_unit(256), "color scale");
    int releases = 0;
    { Lease first(releases); Lease moved(std::move(first)); }
    check(releases == 1, "move release exactly once");
    try { Lease error(releases); throw 1; } catch (int) {}
    check(releases == 2, "error path release");
    for (auto s : {"", "-1", "12x", "4294967296", "99999999999", " 1", "1.0"}) check(!parse_count(s), "parser corpus invalid");
    check(parse_count("4294967295").value() == UINT32_MAX, "parser max bound");
    std::mt19937 generator(0xAEE2026u);
    for (int i = 0; i < 20000; ++i) {
        const std::uint32_t n = generator();
        check(parse_count(std::to_string(n)).value() == n, "parser property roundtrip");
        std::string fuzz;
        const auto length = generator() % 17;
        for (unsigned j = 0; j < length; ++j) fuzz.push_back(static_cast<char>(generator() % 256));
        auto parsed = parse_count(fuzz);
        if (parsed) {
            bool valid = !fuzz.empty() && fuzz.size() <= 10;
            std::uint64_t oracle = 0;
            for (unsigned char c : fuzz) { valid = valid && c >= '0' && c <= '9'; oracle = oracle * 10 + (c >= '0' && c <= '9' ? c - '0' : 0); }
            check(valid && oracle <= UINT32_MAX && oracle == *parsed, "parser fuzz accepted malformed");
        }
        const std::size_t w = generator() % 127 + 1, h = generator() % 127 + 1;
        const std::size_t stride = w * 4 + (generator() % 32), x = generator() % (w + 2), y = generator() % (h + 2);
        auto offset = pixel_offset(x, y, w, h, stride, stride * h);
        check(bool(offset) == (x < w && y < h), "geometry property bounds");
        if (offset) check(*offset == y * stride + x * 4 && *offset + 4 <= stride * h, "geometry property offset");
        const double frame = int(generator() % 100000) - 50000, fps = generator() % 120 + 1;
        auto seconds = to_seconds({frame}, {fps});
        check(seconds && std::abs(seconds->value * fps - frame) <= 1e-10, "time property inverse");
        State state = State::idle;
        for (int j = 0; j < 12; ++j) {
            Event event = static_cast<Event>(generator() % 4);
            auto next = transition(state, event);
            if (next) state = *next;
            if (event == Event::cancel) check(state == State::canceled, "state cancel invariant");
            if (state == State::canceled) check(!transition(state, Event::acquire), "state canceled cannot acquire");
        }
    }
    std::cout << "seed=0xAEE2026 iterations=20000 failures=" << failures << '\n';
    return failures ? 1 : 0;
}
