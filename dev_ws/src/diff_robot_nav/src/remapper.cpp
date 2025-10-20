#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist_stamped.hpp"

class CmdVelRemapper : public rclcpp::Node
{
public:
    CmdVelRemapper()
    : Node("cmd_vel_remapper")
    {
        // Publisher to the diff_drive_controller topic
        pub_ = this->create_publisher<geometry_msgs::msg::TwistStamped>(
            "/diff_drive_controller/cmd_vel", 10);

        // Subscriber to your generic cmd_vel
        sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "/cmd_vel", 10,
            std::bind(&CmdVelRemapper::cmdVelCallback, this, std::placeholders::_1)
        );

        RCLCPP_INFO(this->get_logger(), "CmdVel Remapper Node Started");
    }

private:
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
    {
        geometry_msgs::msg::TwistStamped stamped_msg;
        stamped_msg.header.stamp = this->now();
        stamped_msg.header.frame_id = "base_footprint";  // or whichever frame your controller expects
        stamped_msg.twist = *msg;

        pub_->publish(stamped_msg);
    }

    rclcpp::Publisher<geometry_msgs::msg::TwistStamped>::SharedPtr pub_;
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr sub_;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CmdVelRemapper>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
