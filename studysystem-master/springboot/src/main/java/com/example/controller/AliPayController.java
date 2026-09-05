package com.example.controller;


import cn.hutool.core.date.DateUtil;
import cn.hutool.json.JSONObject;
import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.internal.util.AlipaySignature;
import com.alipay.api.request.AlipayTradePagePayRequest;
import com.example.common.Result;
import com.example.common.config.AliPayConfig;
import com.example.entity.Account;
import com.example.entity.Orders;
import com.example.entity.RechargeRecord;
import com.example.entity.User;
import com.example.service.OrdersService;
import com.example.service.RechargeRecordService;
import com.example.service.UserService;
import com.example.utils.TokenUtils;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

//  https://natapp.cn/
// ekihat7647@sandbox.com
@RestController
@RequestMapping("/alipay")
public class AliPayController {

    // 支付宝沙箱网关地址
    private static final String GATEWAY_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do";
    private static final String FORMAT = "JSON";
    private static final String CHARSET = "UTF-8";
    //签名方式
    private static final String SIGN_TYPE = "RSA2";

    @Resource
    private AliPayConfig aliPayConfig;

    @Resource
    private OrdersService ordersService;

    @Resource
    private UserService userService;

    @Resource
    private RechargeRecordService rechargeRecordService;

    @GetMapping("/pay")  //  /alipay/pay?orderNo=xxx
    public Result pay(Double price, HttpServletResponse httpResponse) throws Exception {
        // 查询订单信息
        RechargeRecord rechargeRecord = new RechargeRecord();
//        Orders orders = ordersService.selectByOrderNo(orderNo);
//        if (orders == null) {
//            return;
//        }
        Account account = TokenUtils.getCurrentUser();
        User user = new User();
        user = userService.selectById(account.getId());
        rechargeRecord.setPrice(price);
        rechargeRecord.setRecordid(DateUtil.format(new Date(),"yyyyMMddHHmmss"));
        rechargeRecord.setTime(DateUtil.now());
        rechargeRecord.setUserId(account.getId());
        rechargeRecord.setMethod("支付宝");


        rechargeRecordService.add(rechargeRecord);
        // 1. 创建Client，通用SDK提供的Client，负责调用支付宝的API
        AlipayClient alipayClient = new DefaultAlipayClient(GATEWAY_URL, aliPayConfig.getAppId(),
                aliPayConfig.getAppPrivateKey(), FORMAT, CHARSET, aliPayConfig.getAlipayPublicKey(), SIGN_TYPE);

        // 2. 创建 Request并设置Request参数
        AlipayTradePagePayRequest request = new AlipayTradePagePayRequest();  // 发送请求的 Request类
        request.setNotifyUrl(aliPayConfig.getNotifyUrl());
        JSONObject bizContent = new JSONObject();
//        bizContent.set("out_trade_no", UUID.randomUUID().toString());  // 我们自己生成的订单编号
//        bizContent.set("total_amount", orders.getTotal()); // 订单的总金额
        bizContent.set("subject", "充值");   // 支付的名称
        bizContent.set("out_trade_no",rechargeRecord.getRecordid());
        bizContent.set("total_amount",price);

        bizContent.set("product_code", "FAST_INSTANT_TRADE_PAY");  // 固定配置
        request.setBizContent(bizContent.toString());
        request.setReturnUrl("http://localhost:8080/front/home"); // 支付完成后自动跳转到本地页面的路径
        // 执行请求，拿到响应的结果，返回给浏览器
        String form = "";
        try {
            form = alipayClient.pageExecute(request).getBody(); // 调用SDK生成表单
        } catch (AlipayApiException e) {
            e.printStackTrace();
        }
//        httpResponse.setContentType("text/html;charset=" + CHARSET);
//        httpResponse.getWriter().write(form);// 直接将完整的表单html输出到页面
//        httpResponse.getWriter().flush();
//        httpResponse.getWriter().close();

        user.setAccount(user.getAccount() + price);

        userService.updateById(user);
        return Result.success(form);
    }

    @PostMapping("/notify")  // 注意这里必须是POST接口
    public void payNotify(HttpServletRequest request) throws Exception {
        if (request.getParameter("trade_status").equals("TRADE_SUCCESS")) {
            System.out.println("=========支付宝异步回调========");

            Map<String, String> params = new HashMap<>();
            Map<String, String[]> requestParams = request.getParameterMap();
            for (String name : requestParams.keySet()) {
                params.put(name, request.getParameter(name));
            }

            String sign = params.get("sign");
            String content = AlipaySignature.getSignCheckContentV1(params);
            boolean checkSignature = AlipaySignature.rsa256CheckContent(content, sign, aliPayConfig.getAlipayPublicKey(), "UTF-8"); // 验证签名
            // 支付宝验签
            if (checkSignature) {
                // 验签通过
                System.out.println("交易名称: " + params.get("subject"));
                System.out.println("交易状态: " + params.get("trade_status"));
                System.out.println("支付宝交易凭证号: " + params.get("trade_no"));
                System.out.println("商户订单号: " + params.get("out_trade_no"));
                System.out.println("交易金额: " + params.get("total_amount"));
                System.out.println("买家在支付宝唯一id: " + params.get("buyer_id"));
                System.out.println("买家付款时间: " + params.get("gmt_payment"));
                System.out.println("买家付款金额: " + params.get("buyer_pay_amount"));


                String tradeNo = params.get("out_trade_no");
                String gmtPayment = params.get("gmt_payment");
                String alipayTradeNo = params.get("trade_no");
                // 更新订单状态为已支付，设置支付信息
//                Orders orders = ordersService.selectByOrderNo(tradeNo);
//                orders.setStatus("已支付");
//                orders.setPayTime(gmtPayment);
//                orders.setPayNo(alipayTradeNo);
//                ordersService.updateById(orders);

            }
        }
    }

}