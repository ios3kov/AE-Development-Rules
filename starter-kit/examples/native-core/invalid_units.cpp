// Expected compile failure: elapsed seconds cannot be passed as a frame count.
#include "native_core.hpp"
int main() {
    auto result = ae_rules_example::to_seconds(ae_rules_example::Seconds{24}, ae_rules_example::FrameRate{24});
    return result ? 0 : 1;
}
