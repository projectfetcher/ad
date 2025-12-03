<?php
/**
 * Plugin Name: AdSense Checker PRO - GitHub Edition
 * Description: Run powerful 2025 AdSense audit using your private Python checker on GitHub/Render
 * Version: 1.0
 * Author: YourName
 */

if (!defined('ABSPATH')) exit;

class AdSenseCheckerGitHub {
    private $option_name = 'adsense_checker_github_settings';
    private $api_url;

    public function __construct() {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('admin_enqueue_scripts', [$this, 'enqueue']);
        add_action('wp_ajax_adsense_run_audit', [$this, 'ajax_run_audit']);
        register_activation_hook(__FILE__, [$this, 'activate']);
    }

    public function activate() {
        add_option($this->option_name, [
            'api_url' => '',
            'username' => 'admin',
            'password' => 'secret2025',
            'auth_header' => 'Basic YWRtaW46c2VjcmV0MjAyNQ==' // base64 of admin:secret2025
        ]);
    }

    public function add_menu() {
        add_menu_page(
            'AdSense Checker',
            'AdSense Checker',
            'manage_options',
            'adsense-checker-github',
            [$this, 'admin_page'],
            'dashicons-money-alt',
            59
        );
    }

    public function enqueue($hook) {
        if ('toplevel_page_adsense-checker-github' !== $hook) return;

        wp_enqueue_style('adsense-checker-css', plugins_url('style.css', __FILE__));
        wp_enqueue_script('adsense-checker-js', plugins_url('script.js', __FILE__), ['jquery'], '1.0', true);
        wp_localize_script('adsense-checker-js', 'adsense_checker', [
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('adsense_checker_nonce')
        ]);
    }

    public function admin_page() {
        $options = get_option($this->option_name);
        ?>
        <div class="wrap">
            <h1>AdSense Checker PRO <small>(GitHub + Python Powered)</small></h1>

            <?php if (!$options['api_url']): ?>
                <div class="notice notice-error">
                    <p>Please configure your Python API URL first.</p>
                </div>
            <?php endif; ?>

            <form method="post" action="options.php">
                <?php settings_fields($this->option_name); ?>
                <table class="form-table">
                    <tr>
                        <th>Python API URL</th>
                        <td><input type="url" name="<?php echo $this->option_name; ?>[api_url]" value="<?php echo esc_attr($options['api_url']); ?>" class="regular-text" placeholder="https://your-checker.onrender.com/audit" required /></td>
                    </tr>
                    <tr>
                        <th>Username</th>
                        <td><input type="text" name="<?php echo $this->option_name; ?>[username]" value="<?php echo esc_attr($options['username']); ?>" /></td>
                    </tr>
                    <tr>
                        <th>Password</th>
                        <td><input type="password" name="<?php echo $this->option_name; ?>[password]" value="<?php echo esc_attr($options['password']); ?>" /></td>
                    </tr>
                </table>
                <?php submit_button('Save Settings'); ?>
            </form>

            <hr>

            <h2>Run Audit</h2>
            <p>Enter your website URL to scan:</p>
            <input type="url" id="site_url" class="regular-text" placeholder="https://yoursite.com" value="<?php echo home_url(); ?>" />
            <button id="run_audit" class="button button-primary button-large">Run Full AdSense Audit</button>

            <div id="audit_result" style="margin-top:20px;"></div>
        </div>
        <?php
    }

    public function ajax_run_audit() {
        check_ajax_referer('adsense_checker_nonce', 'nonce');

        $site_url = sanitize_url($_POST['site_url']);
        $options = get_option($this->option_name);

        if (!$options['api_url']) {
            wp_send_json_error('API URL not configured');
        }

        $response = wp_remote_post($options['api_url'], [
            'headers' => [
                'Authorization' => $options['auth_header'],
                'Content-Type' => 'application/json'
            ],
            'body' => json_encode(['url' => $site_url]),
            'timeout' => 180
        ]);

        if (is_wp_error($response)) {
            wp_send_json_error('Connection failed: ' . $response->get_error_message());
        }

        $body = wp_remote_retrieve_body($response);
        $data = json_decode($body, true);

        if (isset($data['error'])) {
            wp_send_json_error('API Error: ' . $data['error']);
        }

        wp_send_json_success([
            'output' => '<pre style="background:#f0f0f0;padding:15px;border-radius:8px;overflow:auto;">' . esc_html($data['result']) . '</pre>'
        ]);
    }
}

new AdSenseCheckerGitHub();

// Register settings
add_action('admin_init', function() {
    register_setting('adsense_checker_github_settings', 'adsense_checker_github_settings');
});
